from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Protocol


class ReferenceAcquisitionDiagnosticCode(StrEnum):
    INVALID_URL = "invalid_url"
    UNSUPPORTED_SCHEME = "unsupported_scheme"
    CREDENTIALS_NOT_ALLOWED = "credentials_not_allowed"
    NETWORK_TARGET_REJECTED = "network_target_rejected"
    REDIRECT_REJECTED = "redirect_rejected"
    AUTHENTICATION_REQUIRED = "authentication_required"
    PROTECTED_CONTENT = "protected_content"
    POLICY_DISALLOWED = "policy_disallowed"
    UNSUPPORTED_RESOURCE = "unsupported_resource"
    NOT_FOUND = "not_found"
    SIZE_LIMIT_EXCEEDED = "size_limit_exceeded"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    TRANSPORT_FAILED = "transport_failed"
    INTEGRITY_FAILED = "integrity_failed"
    MEDIA_PROBE_FAILED = "media_probe_failed"
    CLEANUP_FAILED = "cleanup_failed"


@dataclass(frozen=True, slots=True)
class ReferenceAcquisitionDiagnostic:
    code: ReferenceAcquisitionDiagnosticCode
    message: str
    retryable: bool = False

    def __post_init__(self) -> None:
        if not self.message.strip():
            raise ValueError("reference acquisition diagnostic message must not be empty")


@dataclass(frozen=True, slots=True)
class ReferenceAcquisitionRequest:
    url: str

    def __post_init__(self) -> None:
        if not self.url.strip():
            raise ValueError("reference acquisition URL must not be empty")


@dataclass(frozen=True, slots=True)
class AcquiredReferenceMedia:
    local_path: Path
    original_url: str
    final_url: str
    provider: str
    provider_item_id: str | None
    retrieved_at: datetime
    content_hash: str
    byte_size: int
    content_type: str | None = None
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("original_url", self.original_url),
            ("final_url", self.final_url),
            ("provider", self.provider),
            ("content_hash", self.content_hash),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if not self.local_path.is_absolute():
            raise ValueError("acquired reference local_path must be absolute")
        if not self.content_hash.startswith("sha256:"):
            raise ValueError("acquired reference content_hash must use sha256:* form")
        if isinstance(self.byte_size, bool) or not isinstance(self.byte_size, int):
            raise TypeError("byte_size must be an int")
        if self.byte_size < 0:
            raise ValueError("byte_size must be >= 0")
        if any(not warning.strip() for warning in self.warnings):
            raise ValueError("warnings must not contain blank values")


@dataclass(frozen=True, slots=True)
class ReferenceAcquisitionResult:
    acquired: AcquiredReferenceMedia | None
    diagnostics: tuple[ReferenceAcquisitionDiagnostic, ...] = ()

    def __post_init__(self) -> None:
        if self.acquired is None and not self.diagnostics:
            raise ValueError("failed acquisition result requires at least one diagnostic")
        if self.acquired is not None and self.diagnostics:
            raise ValueError("successful acquisition result must not contain failure diagnostics")

    @property
    def is_acquired(self) -> bool:
        return self.acquired is not None and not self.diagnostics


class ReferenceAcquisitionPort(Protocol):
    """Acquire transport bytes only; never create Asset or Planning authority."""

    def acquire(self, request: ReferenceAcquisitionRequest) -> ReferenceAcquisitionResult: ...
