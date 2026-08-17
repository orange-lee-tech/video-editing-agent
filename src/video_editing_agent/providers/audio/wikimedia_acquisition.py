from __future__ import annotations

import hashlib
import http.client
import os
import ssl
import tempfile
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import SplitResult, urljoin, urlsplit

from video_editing_agent.application.ports.audio_acquisition import (
    AcquiredAudioMaterial,
    AudioAcquisitionDiagnostic,
    AudioAcquisitionDiagnosticCode,
    AudioAcquisitionRequest,
    AudioAcquisitionResult,
)
from video_editing_agent.domain.asset.rights import RightsEligibility
from video_editing_agent.providers.reference.direct_https import (
    ConnectionFactory,
    DirectHttpsAcquisitionPolicy,
    Resolver,
    _default_connection_factory,
    _default_resolver,
    _file_sha256,
    _public_address,
    _request_target,
    _ResponseLike,
)

_CHUNK_SIZE = 64 * 1024
_REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
_ALLOWED_HOST = "upload.wikimedia.org"
_ALLOWED_GENERIC_AUDIO_TYPES = frozenset({"application/ogg", "application/octet-stream"})
_USER_AGENT = (
    "video-editing-agent-bot/0.1 "
    "(https://github.com/orange-lee-tech/video-editing-agent)"
)
Clock = Callable[[], datetime]
Monotonic = Callable[[], float]


class _AcquisitionFailure(Exception):
    def __init__(
        self,
        code: AudioAcquisitionDiagnosticCode,
        message: str,
        *,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


def _default_clock() -> datetime:
    return datetime.now(UTC)


def _content_type_base(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.partition(";")[0].strip().casefold()
    return normalized or None


class WikimediaAudioAcquirer:
    """Acquire one source-verified Commons audio file; never accepts arbitrary hosts."""

    def __init__(
        self,
        root: Path,
        *,
        policy: DirectHttpsAcquisitionPolicy | None = None,
        resolver: Resolver = _default_resolver,
        connection_factory: ConnectionFactory = _default_connection_factory,
        clock: Clock = _default_clock,
        monotonic: Monotonic = time.monotonic,
    ) -> None:
        self._root = root.expanduser().resolve()
        self._partial_root = self._root / ".partial"
        self._committed_root = self._root / "sha256"
        self._policy = policy or DirectHttpsAcquisitionPolicy(max_bytes=128 * 1024 * 1024)
        self._resolver = resolver
        self._connection_factory = connection_factory
        self._clock = clock
        self._monotonic = monotonic
        self._partial_root.mkdir(parents=True, exist_ok=True)
        self._committed_root.mkdir(parents=True, exist_ok=True)

    def acquire(self, request: AudioAcquisitionRequest) -> AudioAcquisitionResult:
        gate_failure = self._rights_gate(request)
        if gate_failure is not None:
            return AudioAcquisitionResult(None, (gate_failure,))
        try:
            acquired = self._acquire(request)
        except _AcquisitionFailure as failure:
            return AudioAcquisitionResult(
                None,
                (
                    AudioAcquisitionDiagnostic(
                        failure.code,
                        failure.message,
                        failure.retryable,
                    ),
                ),
            )
        except (OSError, ssl.SSLError, http.client.HTTPException) as error:
            return AudioAcquisitionResult(
                None,
                (
                    AudioAcquisitionDiagnostic(
                        AudioAcquisitionDiagnosticCode.TRANSPORT_FAILED,
                        f"Wikimedia audio transport failed: {error}",
                        True,
                    ),
                ),
            )
        return AudioAcquisitionResult(acquired)

    @staticmethod
    def _rights_gate(request: AudioAcquisitionRequest) -> AudioAcquisitionDiagnostic | None:
        if request.provider != "wikimedia_commons" or not request.license_snapshot_ref.startswith(
            "art_sha256_"
        ):
            return AudioAcquisitionDiagnostic(
                AudioAcquisitionDiagnosticCode.CANDIDATE_NOT_VERIFIED,
                "audio acquisition requires a verified Wikimedia rights artifact",
            )
        if request.rights_eligibility is RightsEligibility.INELIGIBLE:
            return AudioAcquisitionDiagnostic(
                AudioAcquisitionDiagnosticCode.RIGHTS_INELIGIBLE,
                "ineligible audio cannot enter automatic acquisition",
            )
        if request.rights_eligibility is RightsEligibility.UNKNOWN:
            return AudioAcquisitionDiagnostic(
                AudioAcquisitionDiagnosticCode.RIGHTS_UNKNOWN,
                "unknown audio rights cannot enter automatic acquisition",
            )
        return None

    def _acquire(self, request: AudioAcquisitionRequest) -> AcquiredAudioMaterial:
        current_url = request.approved_source_url.strip()
        deadline = self._monotonic() + self._policy.total_timeout_seconds
        redirects = 0

        while True:
            if self._monotonic() > deadline:
                raise _AcquisitionFailure(
                    AudioAcquisitionDiagnosticCode.TIME_LIMIT_EXCEEDED,
                    "Wikimedia audio acquisition exceeded the configured total time limit",
                    retryable=True,
                )
            hostname, port, pinned_ip = self._validated_target(
                current_url,
                redirect=redirects > 0,
            )
            connection = self._connection_factory(
                hostname,
                pinned_ip,
                port,
                self._policy.socket_timeout_seconds,
            )
            response = None
            try:
                connection.request(
                    "GET",
                    _request_target(current_url),
                    headers={
                        "Accept": "audio/*,application/ogg;q=0.9,application/octet-stream;q=0.5",
                        "Accept-Encoding": "identity",
                        "Connection": "close",
                        "User-Agent": _USER_AGENT,
                    },
                )
                response = connection.getresponse()
                if response.status in _REDIRECT_STATUSES:
                    location = response.getheader("Location")
                    if location is None or not location.strip():
                        raise _AcquisitionFailure(
                            AudioAcquisitionDiagnosticCode.REDIRECT_REJECTED,
                            "Wikimedia audio redirect omitted a Location target",
                        )
                    if redirects >= self._policy.max_redirects:
                        raise _AcquisitionFailure(
                            AudioAcquisitionDiagnosticCode.REDIRECT_REJECTED,
                            "Wikimedia audio acquisition exceeded the redirect limit",
                        )
                    next_url = urljoin(current_url, location.strip())
                    self._validate_url_shape(next_url, redirect=True)
                    current_url = next_url
                    redirects += 1
                    continue
                if response.status == 404:
                    raise _AcquisitionFailure(
                        AudioAcquisitionDiagnosticCode.SOURCE_FILE_MISSING,
                        "verified Wikimedia audio file is no longer available",
                    )
                if response.status == 429:
                    retry_after = response.getheader("Retry-After")
                    suffix = "" if retry_after is None else f"; Retry-After={retry_after.strip()}"
                    raise _AcquisitionFailure(
                        AudioAcquisitionDiagnosticCode.TRANSPORT_FAILED,
                        f"Wikimedia audio server throttled the request with HTTP 429{suffix}",
                        retryable=True,
                    )
                if response.status != 200:
                    raise _AcquisitionFailure(
                        AudioAcquisitionDiagnosticCode.TRANSPORT_FAILED,
                        f"Wikimedia audio server returned HTTP {response.status}",
                        retryable=response.status >= 500,
                    )

                content_type = _content_type_base(response.getheader("Content-Type"))
                if content_type is None or (
                    not content_type.startswith("audio/")
                    and content_type not in _ALLOWED_GENERIC_AUDIO_TYPES
                ):
                    raise _AcquisitionFailure(
                        AudioAcquisitionDiagnosticCode.UNSUPPORTED_MEDIA_TYPE,
                        f"verified Wikimedia URL did not return audio media ({content_type})",
                    )
                if (
                    request.expected_content_type is not None
                    and content_type != request.expected_content_type.strip().casefold()
                ):
                    raise _AcquisitionFailure(
                        AudioAcquisitionDiagnosticCode.SOURCE_METADATA_CHANGED,
                        "Wikimedia audio MIME type changed after rights verification",
                    )
                declared_length = self._declared_length(response)
                if declared_length is not None and declared_length > self._policy.max_bytes:
                    raise _AcquisitionFailure(
                        AudioAcquisitionDiagnosticCode.SIZE_LIMIT_EXCEEDED,
                        "Wikimedia audio exceeds the configured byte limit",
                    )
                if (
                    declared_length is not None
                    and request.expected_byte_size is not None
                    and declared_length != request.expected_byte_size
                ):
                    raise _AcquisitionFailure(
                        AudioAcquisitionDiagnosticCode.SOURCE_METADATA_CHANGED,
                        "Wikimedia audio byte size changed after rights verification",
                    )
                return self._commit_response(
                    response,
                    request=request,
                    final_url=current_url,
                    content_type=content_type,
                    deadline=deadline,
                )
            except TimeoutError as error:
                raise _AcquisitionFailure(
                    AudioAcquisitionDiagnosticCode.TIME_LIMIT_EXCEEDED,
                    f"Wikimedia audio network operation timed out: {error}",
                    retryable=True,
                ) from error
            finally:
                if response is not None:
                    response.close()
                connection.close()

    def _validated_target(self, url: str, *, redirect: bool) -> tuple[str, int, str]:
        parts = self._validate_url_shape(url, redirect=redirect)
        assert parts.hostname is not None
        hostname = parts.hostname
        try:
            port = parts.port or 443
        except ValueError as error:
            raise _AcquisitionFailure(
                AudioAcquisitionDiagnosticCode.REDIRECT_REJECTED
                if redirect
                else AudioAcquisitionDiagnosticCode.NETWORK_TARGET_REJECTED,
                "Wikimedia audio URL contains an invalid port",
            ) from error
        if port != 443:
            raise _AcquisitionFailure(
                AudioAcquisitionDiagnosticCode.REDIRECT_REJECTED
                if redirect
                else AudioAcquisitionDiagnosticCode.NETWORK_TARGET_REJECTED,
                "Wikimedia audio acquisition permits HTTPS port 443 only",
            )
        try:
            addresses = self._resolver(hostname, port)
        except OSError as error:
            raise _AcquisitionFailure(
                AudioAcquisitionDiagnosticCode.TRANSPORT_FAILED,
                f"Wikimedia hostname resolution failed: {error}",
                retryable=True,
            ) from error
        public = tuple(address for address in addresses if _public_address(address))
        if not public:
            raise _AcquisitionFailure(
                AudioAcquisitionDiagnosticCode.REDIRECT_REJECTED
                if redirect
                else AudioAcquisitionDiagnosticCode.NETWORK_TARGET_REJECTED,
                "Wikimedia audio host did not resolve to an allowed public address",
            )
        return hostname, port, public[0]

    @staticmethod
    def _validate_url_shape(url: str, *, redirect: bool) -> SplitResult:
        try:
            parts = urlsplit(url)
        except ValueError as error:
            raise _AcquisitionFailure(
                AudioAcquisitionDiagnosticCode.REDIRECT_REJECTED
                if redirect
                else AudioAcquisitionDiagnosticCode.NETWORK_TARGET_REJECTED,
                "Wikimedia audio URL could not be parsed",
            ) from error
        if (
            parts.scheme.casefold() != "https"
            or parts.hostname != _ALLOWED_HOST
            or parts.username is not None
            or parts.password is not None
        ):
            raise _AcquisitionFailure(
                AudioAcquisitionDiagnosticCode.REDIRECT_REJECTED
                if redirect
                else AudioAcquisitionDiagnosticCode.NETWORK_TARGET_REJECTED,
                "Wikimedia audio acquisition only permits upload.wikimedia.org HTTPS URLs",
            )
        return parts

    @staticmethod
    def _declared_length(response: _ResponseLike) -> int | None:
        raw = response.getheader("Content-Length")
        if raw is None:
            return None
        try:
            value = int(raw)
        except (TypeError, ValueError):
            return None
        return value if value >= 0 else None

    def _commit_response(
        self,
        response: _ResponseLike,
        *,
        request: AudioAcquisitionRequest,
        final_url: str,
        content_type: str,
        deadline: float,
    ) -> AcquiredAudioMaterial:
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=self._partial_root,
                prefix=".wikimedia-audio-",
                suffix=".part",
                delete=False,
            ) as stream:
                temporary_path = Path(stream.name)
                sha256 = hashlib.sha256()
                sha1 = hashlib.sha1()  # noqa: S324 - provider integrity comparison, not security
                byte_size = 0
                while True:
                    if self._monotonic() > deadline:
                        raise _AcquisitionFailure(
                            AudioAcquisitionDiagnosticCode.TIME_LIMIT_EXCEEDED,
                            "Wikimedia audio acquisition exceeded the configured total time limit",
                            retryable=True,
                        )
                    chunk = response.read(_CHUNK_SIZE)
                    if not chunk:
                        break
                    if not isinstance(chunk, bytes):
                        raise _AcquisitionFailure(
                            AudioAcquisitionDiagnosticCode.TRANSPORT_FAILED,
                            "Wikimedia audio response returned non-byte content",
                        )
                    byte_size += len(chunk)
                    if byte_size > self._policy.max_bytes:
                        raise _AcquisitionFailure(
                            AudioAcquisitionDiagnosticCode.SIZE_LIMIT_EXCEEDED,
                            "Wikimedia audio exceeds the configured byte limit",
                        )
                    sha256.update(chunk)
                    sha1.update(chunk)
                    stream.write(chunk)
                stream.flush()
                os.fsync(stream.fileno())

            if request.expected_byte_size is not None and byte_size != request.expected_byte_size:
                raise _AcquisitionFailure(
                    AudioAcquisitionDiagnosticCode.SOURCE_METADATA_CHANGED,
                    "Wikimedia audio byte size changed during acquisition",
                )
            source_sha1 = sha1.hexdigest()
            if (
                request.expected_source_sha1 is not None
                and source_sha1 != request.expected_source_sha1.strip().casefold()
            ):
                raise _AcquisitionFailure(
                    AudioAcquisitionDiagnosticCode.SOURCE_HASH_MISMATCH,
                    "Wikimedia audio SHA-1 no longer matches verified source metadata",
                )

            digest_hex = sha256.hexdigest()
            destination = self._committed_root / digest_hex[:2] / f"{digest_hex}.media"
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                if (
                    destination.stat().st_size != byte_size
                    or _file_sha256(destination) != digest_hex
                ):
                    raise _AcquisitionFailure(
                        AudioAcquisitionDiagnosticCode.INTEGRITY_FAILED,
                        "existing provider audio failed content-address integrity validation",
                    )
                temporary_path.unlink()
                temporary_path = None
            else:
                os.replace(temporary_path, destination)
                temporary_path = None
                if (
                    destination.stat().st_size != byte_size
                    or _file_sha256(destination) != digest_hex
                ):
                    destination.unlink(missing_ok=True)
                    raise _AcquisitionFailure(
                        AudioAcquisitionDiagnosticCode.INTEGRITY_FAILED,
                        "committed provider audio failed content-address integrity validation",
                    )

            return AcquiredAudioMaterial(
                provider=request.provider,
                provider_item_id=request.provider_item_id,
                local_path=destination.resolve(),
                source_page=request.source_page,
                final_source_url=final_url,
                acquired_at=self._clock(),
                byte_size=byte_size,
                local_sha256=f"sha256:{digest_hex}",
                content_type=content_type,
                license_snapshot_ref=request.license_snapshot_ref,
                source_sha1=source_sha1,
            )
        except _AcquisitionFailure as failure:
            self._cleanup_partial(temporary_path, failure)
            raise
        except OSError as error:
            write_failure = _AcquisitionFailure(
                AudioAcquisitionDiagnosticCode.TRANSPORT_FAILED,
                f"provider audio write failed: {error}",
                retryable=True,
            )
            self._cleanup_partial(temporary_path, write_failure)
            raise write_failure from error

    @staticmethod
    def _cleanup_partial(path: Path | None, failure: _AcquisitionFailure) -> None:
        if path is None or not path.exists():
            return
        try:
            path.unlink()
        except OSError as cleanup_error:
            raise _AcquisitionFailure(
                AudioAcquisitionDiagnosticCode.CLEANUP_FAILED,
                f"{failure.message}; partial cleanup also failed: {cleanup_error}",
            ) from failure
