from __future__ import annotations

import ctypes
import json
import re
import sys
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit

from video_editing_agent.application.ports.visual_understanding import VisualProviderQuotaError
from video_editing_agent.application.use_cases.product_flow import (
    ProductFlowEvent,
    ProductFlowEventLevel,
    ProductFlowStage,
)

_HTTPS_URL = re.compile(r"https://[^\s<>\"'，。；：！？【】《》]+", re.IGNORECASE)
_TRAILING_PROSE = ").,;:!?]}，。；：！？】》"
_PROFILE_VERSION = "video-editing-agent-profile-v1"
_SECRET_FIELDS = frozenset({"thinking_key", "visual_key", "api_key", "secret"})


def extract_first_https_url(value: str) -> str | None:
    """Extract one bounded HTTPS URL from ordinary share text."""

    match = _HTTPS_URL.search(value)
    if match is None:
        return None
    candidate = match.group(0).rstrip(_TRAILING_PROSE)
    parts = urlsplit(candidate)
    if parts.scheme.casefold() != "https" or not parts.hostname:
        return None
    return candidate


def default_profile_root(home: Path | None = None) -> Path:
    base = home if home is not None else Path.home()
    return base / "Documents" / "Video Editing Agent" / "Profiles"


def serialize_profile(kind: str, values: Mapping[str, str]) -> str:
    if not kind.strip():
        raise ValueError("profile kind must not be empty")
    forbidden = _SECRET_FIELDS.intersection(values)
    if forbidden:
        raise ValueError("plaintext secret fields are forbidden in profile files")
    lines = [f"schema={_PROFILE_VERSION}", f"kind={kind.strip()}"]
    lines.extend(
        f"{key}={json.dumps(value, ensure_ascii=False)}"
        for key, value in sorted(values.items())
        if value.strip()
    )
    return "\n".join(lines) + "\n"


def parse_profile(content: str, expected_kind: str) -> dict[str, str]:
    lines = content.splitlines()
    if len(lines) < 2 or lines[0] != f"schema={_PROFILE_VERSION}":
        raise ValueError("unsupported profile schema")
    if lines[1] != f"kind={expected_kind}":
        raise ValueError("profile kind does not match this form")
    values: dict[str, str] = {}
    for line in lines[2:]:
        key, separator, encoded = line.partition("=")
        if not separator or not key or key in values or key in _SECRET_FIELDS:
            raise ValueError("invalid or forbidden profile field")
        value = json.loads(encoded)
        if not isinstance(value, str):
            raise ValueError("profile values must be strings")
        values[key] = value
    return values


class ProtectedCredentialStore:
    """User-scoped Windows DPAPI storage; no non-Windows plaintext fallback."""

    def __init__(self, root: Path, *, platform: str | None = None) -> None:
        self._root = root.expanduser().resolve() / ".credentials"
        self._platform = sys.platform if platform is None else platform

    @property
    def available(self) -> bool:
        return self._platform == "win32"

    def save(self, secret: str, credential_id: str | None = None) -> str:
        if not self.available:
            raise RuntimeError("protected credential persistence is unavailable on this platform")
        if not secret:
            raise ValueError("credential must not be empty")
        identifier = credential_id or f"credential-{uuid.uuid4().hex}"
        if not re.fullmatch(r"credential-[0-9a-f]{32}", identifier):
            raise ValueError("invalid credential identifier")
        protected = _dpapi_protect(secret.encode("utf-8"))
        self._root.mkdir(parents=True, exist_ok=True)
        (self._root / f"{identifier}.bin").write_bytes(protected)
        return identifier

    def load(self, credential_id: str) -> str:
        if not self.available:
            raise RuntimeError("protected credential persistence is unavailable on this platform")
        path = self._credential_path(credential_id)
        return _dpapi_unprotect(path.read_bytes()).decode("utf-8")

    def delete(self, credential_id: str) -> None:
        self._credential_path(credential_id).unlink(missing_ok=True)

    def _credential_path(self, credential_id: str) -> Path:
        if not re.fullmatch(r"credential-[0-9a-f]{32}", credential_id):
            raise ValueError("invalid credential identifier")
        return self._root / f"{credential_id}.bin"


def save_api_profile(
    path: Path,
    *,
    visual_provider: str,
    thinking_key: str,
    visual_key: str,
    credentials: ProtectedCredentialStore,
) -> None:
    if not credentials.available:
        raise RuntimeError("protected credential persistence is unavailable on this platform")
    previous: dict[str, str] = {}
    if path.exists():
        previous = parse_profile(path.read_text(encoding="utf-8"), "api")
    thinking_ref = credentials.save(thinking_key, previous.get("thinking_credential_ref"))
    visual_ref = credentials.save(visual_key, previous.get("visual_credential_ref"))
    content = serialize_profile(
        "api",
        {
            "visual_provider": visual_provider,
            "thinking_credential_ref": thinking_ref,
            "visual_credential_ref": visual_ref,
        },
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_api_profile(path: Path, credentials: ProtectedCredentialStore) -> tuple[str, str, str]:
    values = parse_profile(path.read_text(encoding="utf-8"), "api")
    return (
        values.get("visual_provider", "gemini"),
        credentials.load(values["thinking_credential_ref"]),
        credentials.load(values["visual_credential_ref"]),
    )


def delete_api_profile(path: Path, credentials: ProtectedCredentialStore) -> None:
    if path.exists():
        values = parse_profile(path.read_text(encoding="utf-8"), "api")
        for key in ("thinking_credential_ref", "visual_credential_ref"):
            identifier = values.get(key)
            if identifier:
                credentials.delete(identifier)
        path.unlink()


class _DataBlob(ctypes.Structure):
    _fields_ = [("cbData", ctypes.c_ulong), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]


def _blob(data: bytes) -> tuple[_DataBlob, ctypes.Array[ctypes.c_char]]:
    buffer = ctypes.create_string_buffer(data)
    return (
        _DataBlob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte))),
        buffer,
    )


def _dpapi_protect(data: bytes) -> bytes:
    source, source_buffer = _blob(data)
    output = _DataBlob()
    crypt32 = ctypes.windll.crypt32  # type: ignore[attr-defined, unused-ignore]
    kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined, unused-ignore]
    if not crypt32.CryptProtectData(
        ctypes.byref(source), None, None, None, None, 0, ctypes.byref(output)
    ):
        raise ctypes.WinError()  # type: ignore[attr-defined, unused-ignore]
    del source_buffer
    try:
        return ctypes.string_at(output.pbData, output.cbData)
    finally:
        kernel32.LocalFree(output.pbData)


def _dpapi_unprotect(data: bytes) -> bytes:
    source, source_buffer = _blob(data)
    output = _DataBlob()
    crypt32 = ctypes.windll.crypt32  # type: ignore[attr-defined, unused-ignore]
    kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined, unused-ignore]
    if not crypt32.CryptUnprotectData(
        ctypes.byref(source), None, None, None, None, 0, ctypes.byref(output)
    ):
        raise ctypes.WinError()  # type: ignore[attr-defined, unused-ignore]
    del source_buffer
    try:
        return ctypes.string_at(output.pbData, output.cbData)
    finally:
        kernel32.LocalFree(output.pbData)


_STAGE_LABELS = {
    "zh-CN": {
        ProductFlowStage.PROJECT_READY: "项目已就绪",
        ProductFlowStage.INPUT_VALIDATION: "正在验证输入",
        ProductFlowStage.INGEST_UNDERSTANDING: "正在分析媒体",
        ProductFlowStage.MUSIC_PREPARATION: "正在准备音乐",
        ProductFlowStage.PLANNING_GENERATION: "正在生成并复审方案",
        ProductFlowStage.EDITING_DECISION: "正在生成剪辑决策",
        ProductFlowStage.RESOLVING: "正在匹配真实素材",
        ProductFlowStage.EDL_ASSEMBLY: "正在组装剪辑时间线",
        ProductFlowStage.AUDIO_ASSEMBLY: "正在组装原声与音频",
        ProductFlowStage.VOICE_PREPARATION: "正在准备人声",
        ProductFlowStage.SUBTITLE_COMPILATION: "正在生成可信字幕",
        ProductFlowStage.RENDERING: "正在渲染视频",
        ProductFlowStage.REVIEW_QC: "正在检查成片",
        ProductFlowStage.COMPLETED: "已完成",
        ProductFlowStage.CORRECTION_REQUIRED: "需要修正",
        ProductFlowStage.FAILED: "任务失败",
    },
    "en": {stage: stage.value.replace("_", " ").title() for stage in ProductFlowStage},
}

_EVENT_MESSAGES_ZH = {
    "Project is open and ready": "项目已打开并准备就绪",
    "Planning input accepted": "拍摄规划输入已通过校验",
    "Editing input accepted": "自动剪辑输入已通过校验",
    "Acquiring and analyzing reference-only media": "正在获取并分析仅用于参考的媒体",
    "Generating and validating ScriptPlan": "正在生成并复审脚本方案",
    "Generating and validating ShootingPlan": "正在生成并复审拍摄方案",
    "Planning flow completed": "拍摄规划已完成",
    "Ingesting and understanding local media": "正在导入并理解本地素材",
    "Preparing rights-attested local music": "正在准备已确认使用权的本地音乐",
    "Selecting rights-verified public background music": "正在选择通过权利核验的公共背景音乐",
    "Generating and persisting EditPlan": "正在生成并保存剪辑决策",
    "Resolving grounded source selections": "正在根据真实素材匹配剪辑镜头",
    "Some planned edit beats were not grounded; adapting the EditPlan to available local footage": (
        "部分计划镜头未能匹配真实素材，正在根据现有本地素材调整剪辑方案"
    ),
    "Building canonical EDL": "正在组装正式剪辑时间线",
    "Validating canonical source-audio and background-music lanes": "正在检查原声与背景音乐轨道",
    "Preserving grounded original source voice": "正在保留真实素材中的原声",
    "Preparing requested synthetic voice": "正在准备所请求的合成人声",
    (
        "Compiling trusted speech evidence into canonical subtitle timing"
    ): "正在根据可信语音证据生成字幕时间",
    "Rendering canonical EDL": "正在渲染正式剪辑时间线",
    "Reviewing delivered output": "正在检查最终成片",
    "Editing flow completed": "自动剪辑已完成",
    "Review passed without output": "成片检查通过，但未找到输出文件",
    "Public music query produced no candidates; trying the next bounded fallback": (
        "当前公共音乐检索没有候选，正在尝试下一组有限备用检索"
    ),
    "Candidate did not pass the attribution-free automatic rights gate": (
        "候选音乐未通过无需署名的自动权利门槛"
    ),
    "Candidate failed rights verification": "候选音乐权利核验失败",
    "Candidate passed the public music rights gate": "候选音乐已通过公共音乐权利门槛",
    "Acquiring rights-approved public music": "正在获取已通过权利核验的公共音乐",
    "Public music acquisition completed": "公共音乐获取完成",
    (
        "Subtitle stage SKIPPED: no trusted speech transcript or grounded speech requirement; "
        "no subtitle cues were fabricated"
    ): "字幕阶段已跳过：没有可信语音转写或已落地的语音要求，因此未虚构字幕",
}


def localized_stage(stage: ProductFlowStage, language: str) -> str:
    return _STAGE_LABELS.get(language, _STAGE_LABELS["en"])[stage]


def _localized_event_message(event: ProductFlowEvent, language: str) -> str:
    if language != "zh-CN":
        return event.message
    exact = _EVENT_MESSAGES_ZH.get(event.message)
    if exact is not None:
        return exact
    patterns: tuple[tuple[str, str], ...] = (
        (
            r"Public music query (\d+) returned (\d+) candidate\(s\)",
            "公共音乐检索第 {0} 组返回 {1} 个候选",
        ),
        (
            r"Public music discovery produced (\d+) unique candidate\(s\)",
            "公共音乐检索共得到 {0} 个不重复候选",
        ),
        (
            r"Rights gate checking public music candidate (\d+)/(\d+)",
            "正在核验公共音乐候选 {0}/{1}",
        ),
        (
            r"BeatMap analysis completed with (\d+) beat point\(s\)",
            "节拍分析完成，共识别 {0} 个节拍点",
        ),
    )
    for pattern, template in patterns:
        match = re.fullmatch(pattern, event.message)
        if match is not None:
            return template.format(*match.groups())
    if event.level is ProductFlowEventLevel.ERROR:
        return "当前阶段未能完成，请查看错误提示中的处理建议"
    if event.level is ProductFlowEventLevel.WARNING:
        return "当前阶段出现可恢复警告，系统将按安全边界继续处理"
    return "当前阶段处理中"


def format_product_event(event: ProductFlowEvent, language: str) -> str:
    if language == "zh-CN":
        severity = {
            ProductFlowEventLevel.INFO: "",
            ProductFlowEventLevel.WARNING: " 警告",
            ProductFlowEventLevel.ERROR: " 错误",
        }[event.level]
    else:
        severity = (
            "" if event.level is ProductFlowEventLevel.INFO else f" {event.level.value.upper()}"
        )
    return (
        f"[{localized_stage(event.stage, language)}{severity}] "
        f"{_localized_event_message(event, language)}"
    )


def localized_error(error: BaseException, language: str) -> tuple[str, str]:
    detail = str(error).strip()
    lowered = detail.casefold()
    if isinstance(error, VisualProviderQuotaError):
        primary = (
            "Gemini 当日请求额度已耗尽，短时间自动重试无法恢复。请等待额度重置、提高 Gemini 额度，"
            "或在“设置 → 视觉 API 提供方”切换到 OpenAI 后重试。"
            if language == "zh-CN"
            else "The Gemini daily request quota is exhausted and short retries cannot recover it. "
            "Wait for quota reset, raise the Gemini quota, or switch the Visual API Provider "
            "in Settings to OpenAI before retrying."
        )
    elif "429" in lowered or "quota" in lowered or "rate limit" in lowered:
        primary = (
            "视觉理解服务当前达到短时请求限制，本次任务已停止。请按错误提示等待后重试。"
            if language == "zh-CN"
            else "The visual-understanding service reached a short-term request limit. "
            "Wait for the provider retry window and try again."
        )
    elif isinstance(error, (ValueError, FileNotFoundError)):
        primary = (
            "请检查输入内容和文件路径。"
            if language == "zh-CN"
            else "Check the input and file paths."
        )
    else:
        primary = "任务未能完成。" if language == "zh-CN" else "The task could not be completed."
    return primary, detail


@dataclass(slots=True)
class EtaEstimator:
    """Honest ETA based only on observed completed-stage history."""

    stage_seconds: Mapping[str, float]
    started_at: datetime
    observed_elapsed: float = 0.0

    def estimate(self, stage: ProductFlowStage, *, workload: int = 1) -> datetime | None:
        seconds = self.stage_seconds.get(stage.value)
        if seconds is None or seconds <= 0 or workload <= 0:
            return None
        return self.started_at + timedelta(seconds=self.observed_elapsed + seconds * workload)


def format_eta(value: datetime | None, language: str, *, now: datetime | None = None) -> str:
    if value is None:
        return "正在估算…" if language == "zh-CN" else "Estimating…"
    current = now or datetime.now().astimezone()
    minutes = max(1, round((value - current).total_seconds() / 60))
    if language == "zh-CN":
        return f"预计 {value:%H:%M} 完成（约 {minutes} 分钟）"
    return f"Estimated completion {value:%H:%M} (about {minutes} min)"


def save_timing_history(path: Path, values: Mapping[str, float]) -> None:
    safe = {key: float(value) for key, value in values.items() if value > 0}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(safe, sort_keys=True) + "\n", encoding="utf-8")


def load_timing_history(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("timing history must be an object")
    return {
        str(key): float(value)
        for key, value in loaded.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0
    }


def write_utf8_export(path: Path, visible_text: str) -> None:
    with path.expanduser().resolve(strict=False).open("w", encoding="utf-8", newline="") as stream:
        stream.write(visible_text)


def is_placeholder_value(value: str, placeholders: Mapping[str, str]) -> bool:
    return value in placeholders.values()


def profile_filename(kind: str, now: datetime | None = None) -> str:
    moment = now or datetime.now()
    prefix = "API" if kind == "api" else "编导"
    return f"{prefix}-{moment.year}-{moment.month}-{moment.day}.txt"
