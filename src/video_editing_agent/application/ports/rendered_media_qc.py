from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from video_editing_agent.application.ports.executor import DeterministicToolInvocation


class RenderedMediaQcCode(StrEnum):
    NO_AUDIO_STREAM = "no_audio_stream"
    CLIPPING = "clipping"
    MOSTLY_SILENT = "mostly_silent"
    OUTPUT_MISSING = "output_missing"
    INSPECTION_FAILED = "inspection_failed"


@dataclass(frozen=True, slots=True)
class RenderedMediaQcFinding:
    code: RenderedMediaQcCode
    message: str

    def __post_init__(self) -> None:
        if not self.message.strip():
            raise ValueError("message must not be empty")


@dataclass(frozen=True, slots=True)
class RenderedMediaQcResult:
    path: Path
    audio_stream_present: bool | None
    peak_dbfs: float | None
    rms_dbfs: float | None
    silent_fraction: float | None
    clipped_samples: int | None
    findings: tuple[RenderedMediaQcFinding, ...] = ()
    invocations: tuple[DeterministicToolInvocation, ...] = ()

    @property
    def is_inspectable(self) -> bool:
        blocked_codes = {
            RenderedMediaQcCode.OUTPUT_MISSING,
            RenderedMediaQcCode.INSPECTION_FAILED,
        }
        return not any(finding.code in blocked_codes for finding in self.findings)

    def has_code(self, code: RenderedMediaQcCode) -> bool:
        return any(finding.code is code for finding in self.findings)


class RenderedMediaQc(Protocol):
    """Measure delivered media facts only; no editorial or render authority."""

    def inspect(self, path: Path) -> RenderedMediaQcResult: ...
