from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class UntrustedTextSource(StrEnum):
    TRANSCRIPT = "transcript"
    OCR = "ocr"
    SUBTITLE = "subtitle"
    REFERENCE_MEDIA = "reference_media"
    FILENAME_METADATA = "filename_metadata"
    PROVIDER_DESCRIPTION = "provider_description"


@dataclass(frozen=True, slots=True)
class UntrustedText:
    """Media/provider-derived text is evidence data, never executor authority."""

    value: str
    source_kind: UntrustedTextSource
    source_ref: str

    def __post_init__(self) -> None:
        if not self.source_ref.strip():
            raise ValueError("source_ref must not be empty")


@dataclass(frozen=True, slots=True)
class DeterministicToolInvocation:
    """Validated argv-style invocation; no shell command string is accepted."""

    invocation_id: str
    tool_id: str
    arguments: tuple[str, ...]
    input_refs: tuple[str, ...] = ()
    expected_output_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.invocation_id.strip():
            raise ValueError("invocation_id must not be empty")
        if not self.tool_id.strip():
            raise ValueError("tool_id must not be empty")
        if any("\x00" in argument for argument in self.arguments):
            raise ValueError("tool arguments must not contain NUL bytes")


@dataclass(frozen=True, slots=True)
class ToolExecutionResult:
    invocation_id: str
    return_code: int
    output_refs: tuple[str, ...] = ()
    diagnostic: str | None = None


class DeterministicExecutor(Protocol):
    """Execute only typed deterministic invocations created after policy validation."""

    def execute(self, invocation: DeterministicToolInvocation) -> ToolExecutionResult: ...
