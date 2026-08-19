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

from video_editing_agent.application.use_cases.product_flow import ProductFlowStage

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
        ProductFlowStage.PLANNING_GENERATION: "正在生成并复审方案",
        ProductFlowStage.EDITING_DECISION: "正在生成剪辑决策",
        ProductFlowStage.RESOLVING: "正在匹配真实素材",
        ProductFlowStage.EDL_ASSEMBLY: "正在组装剪辑时间线",
        ProductFlowStage.RENDERING: "正在渲染视频",
        ProductFlowStage.REVIEW_QC: "正在检查成片",
        ProductFlowStage.COMPLETED: "已完成",
        ProductFlowStage.CORRECTION_REQUIRED: "需要修正",
        ProductFlowStage.FAILED: "任务失败",
    },
    "en": {stage: stage.value.replace("_", " ").title() for stage in ProductFlowStage},
}


def localized_stage(stage: ProductFlowStage, language: str) -> str:
    return _STAGE_LABELS.get(language, _STAGE_LABELS["en"])[stage]


def localized_error(error: BaseException, language: str) -> tuple[str, str]:
    detail = str(error).strip()
    lowered = detail.casefold()
    if "429" in lowered or "quota" in lowered or "rate limit" in lowered:
        primary = (
            "视觉理解服务当前达到请求/配额限制，本次任务已停止。请稍后重试或检查 API 用量。"
            if language == "zh-CN"
            else "The visual-understanding service reached a request or quota limit. "
            "This run stopped; retry later or check API usage."
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
