from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from video_editing_agent.domain.asset.rights import RightsEligibility


class AudioAcquisitionDiagnosticCode(StrEnum):
    CANDIDATE_NOT_VERIFIED = "candidate_not_verified"
    RIGHTS_INELIGIBLE = "rights_ineligible"
    RIGHTS_UNKNOWN = "rights_unknown"
    SOURCE_METADATA_CHANGED = "source_metadata_changed"
    SOURCE_FILE_MISSING = "source_file_missing"
    SOURCE_HASH_MISMATCH = "source_hash_mismatch"
    UNSUPPORTED_MEDIA_TYPE = "unsupported_media_type"
    NETWORK_TARGET_REJECTED = "network_target_rejected"
    REDIRECT_REJECTED = "redirect_rejected"
    SIZE_LIMIT_EXCEEDED = "size_limit_exceeded"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    TRANSPORT_FAILED = "transport_failed"
    INTEGRITY_FAILED = "integrity_failed"
    CLEANUP_FAILED = "cleanup_failed"


@dataclass(frozen=True, slots=True)
class AudioAcquisitionDiagnostic:
    code: AudioAcquisitionDiagnosticCode
    message: str
    retryable: bool = False

    def __post_init__(self) -> None:
        if not self.message.strip():
            raise ValueError("audio acquisition diagnostic message must not be empty")


@dataclass(frozen=True, slots=True)
class AudioAcquisitionRequest:
    provider: str
    provider_item_id: str
    approved_source_url: str
    source_page: str
    license_snapshot_ref: str
    rights_eligibility: RightsEligibility
    expected_source_sha1: str | None = None
    expected_byte_size: int | None = None
    expected_content_type: str | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("provider", self.provider),
            ("provider_item_id", self.provider_item_id),
            ("approved_source_url", self.approved_source_url),
            ("source_page", self.source_page),
            ("license_snapshot_ref", self.license_snapshot_ref),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if self.expected_source_sha1 is not None:
            normalized = self.expected_source_sha1.strip().casefold()
            if len(normalized) != 40 or any(ch not in "0123456789abcdef" for ch in normalized):
                raise ValueError("expected_source_sha1 must be a 40-character hexadecimal SHA-1")
        if self.expected_byte_size is not None:
            if isinstance(self.expected_byte_size, bool) or not isinstance(
                self.expected_byte_size, int
            ):
                raise TypeError("expected_byte_size must be an int or None")
            if self.expected_byte_size <= 0:
                raise ValueError("expected_byte_size must be > 0")
        if self.expected_content_type is not None and not self.expected_content_type.strip():
            raise ValueError("expected_content_type must not be blank")


@dataclass(frozen=True, slots=True)
class AcquiredAudioMaterial:
    provider: str
    provider_item_id: str
    local_path: Path
    source_page: str
    final_source_url: str
    acquired_at: datetime
    byte_size: int
    local_sha256: str
    content_type: str
    license_snapshot_ref: str
    source_sha1: str | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("provider", self.provider),
            ("provider_item_id", self.provider_item_id),
            ("source_page", self.source_page),
            ("final_source_url", self.final_source_url),
            ("content_type", self.content_type),
            ("license_snapshot_ref", self.license_snapshot_ref),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if not self.local_path.is_absolute():
            raise ValueError("acquired audio local_path must be absolute")
        if not self.local_sha256.startswith("sha256:"):
            raise ValueError("local_sha256 must use sha256:* form")
        if isinstance(self.byte_size, bool) or not isinstance(self.byte_size, int):
            raise TypeError("byte_size must be an int")
        if self.byte_size <= 0:
            raise ValueError("byte_size must be > 0")


@dataclass(frozen=True, slots=True)
class AudioAcquisitionResult:
    acquired: AcquiredAudioMaterial | None
    diagnostics: tuple[AudioAcquisitionDiagnostic, ...] = ()

    def __post_init__(self) -> None:
        if self.acquired is None and not self.diagnostics:
            raise ValueError("failed audio acquisition requires at least one diagnostic")
        if self.acquired is not None and self.diagnostics:
            raise ValueError("successful audio acquisition must not contain diagnostics")

    @property
    def is_acquired(self) -> bool:
        return self.acquired is not None and not self.diagnostics


class AudioAcquisitionPort(Protocol):
    """Acquire one rights-cleared audio item into project-controlled local storage."""

    def acquire(self, request: AudioAcquisitionRequest) -> AudioAcquisitionResult: ...
