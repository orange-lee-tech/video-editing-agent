from __future__ import annotations

import hashlib
import http.client
import ipaddress
import math
import os
import socket
import ssl
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from urllib.parse import SplitResult, urljoin, urlsplit

from video_editing_agent.application.ports.reference_acquisition import (
    AcquiredReferenceMedia,
    ReferenceAcquisitionDiagnostic,
    ReferenceAcquisitionDiagnosticCode,
    ReferenceAcquisitionRequest,
    ReferenceAcquisitionResult,
)

_CHUNK_SIZE = 64 * 1024
_REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
_ALLOWED_GENERIC_CONTENT_TYPES = frozenset({"application/octet-stream"})


@dataclass(frozen=True, slots=True)
class DirectHttpsAcquisitionPolicy:
    max_bytes: int = 512 * 1024 * 1024
    socket_timeout_seconds: float = 30.0
    total_timeout_seconds: float = 180.0
    max_redirects: int = 5

    def __post_init__(self) -> None:
        if isinstance(self.max_bytes, bool) or not isinstance(self.max_bytes, int):
            raise TypeError("max_bytes must be an int")
        if self.max_bytes <= 0:
            raise ValueError("max_bytes must be > 0")
        for name, value in (
            ("socket_timeout_seconds", self.socket_timeout_seconds),
            ("total_timeout_seconds", self.total_timeout_seconds),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number")
            if not math.isfinite(float(value)) or float(value) <= 0:
                raise ValueError(f"{name} must be finite and > 0")
        if isinstance(self.max_redirects, bool) or not isinstance(self.max_redirects, int):
            raise TypeError("max_redirects must be an int")
        if self.max_redirects < 0:
            raise ValueError("max_redirects must be >= 0")


class _ResponseLike(Protocol):
    status: int

    def getheader(self, name: str, default: str | None = None) -> str | None: ...

    def read(self, amt: int | None = None) -> bytes: ...

    def close(self) -> None: ...


class _ConnectionLike(Protocol):
    def request(self, method: str, target: str, *, headers: dict[str, str]) -> None: ...

    def getresponse(self) -> _ResponseLike: ...

    def close(self) -> None: ...


Resolver = Callable[[str, int], tuple[str, ...]]
ConnectionFactory = Callable[[str, str, int, float], _ConnectionLike]
Clock = Callable[[], datetime]
Monotonic = Callable[[], float]


class _AcquisitionFailure(Exception):
    def __init__(
        self,
        code: ReferenceAcquisitionDiagnosticCode,
        message: str,
        *,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, hostname: str, pinned_ip: str, port: int, timeout: float) -> None:
        self._pinned_ip = pinned_ip
        self._tls_context = ssl.create_default_context()
        super().__init__(
            hostname,
            port=port,
            timeout=timeout,
            context=self._tls_context,
        )

    def connect(self) -> None:
        raw_socket = socket.create_connection(
            (self._pinned_ip, self.port),
            self.timeout,
            self.source_address,
        )
        try:
            self.sock = self._tls_context.wrap_socket(raw_socket, server_hostname=self.host)
        except Exception:
            raw_socket.close()
            raise


class _PinnedConnection:
    def __init__(self, hostname: str, pinned_ip: str, port: int, timeout: float) -> None:
        self._connection = _PinnedHTTPSConnection(hostname, pinned_ip, port, timeout)

    def request(self, method: str, target: str, *, headers: dict[str, str]) -> None:
        self._connection.request(method, target, headers=headers)

    def getresponse(self) -> _ResponseLike:
        return self._connection.getresponse()

    def close(self) -> None:
        self._connection.close()


def _default_resolver(hostname: str, port: int) -> tuple[str, ...]:
    addresses: list[str] = []
    for info in socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM):
        address = info[4][0]
        if address not in addresses:
            addresses.append(address)
    return tuple(addresses)


def _default_connection_factory(
    hostname: str, pinned_ip: str, port: int, timeout: float
) -> _ConnectionLike:
    return _PinnedConnection(hostname, pinned_ip, port, timeout)


def _default_clock() -> datetime:
    return datetime.now(UTC)


def _public_address(address: str) -> bool:
    try:
        return ipaddress.ip_address(address).is_global
    except ValueError:
        return False


def _content_type_base(value: str | None) -> str | None:
    if value is None:
        return None
    base = value.partition(";")[0].strip().casefold()
    return base or None


def _request_target(url: str) -> str:
    parts = urlsplit(url)
    target = parts.path or "/"
    if parts.query:
        target = f"{target}?{parts.query}"
    return target


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(_CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


class DirectHttpsReferenceAcquirer:
    """Bounded public-HTTPS acquisition with pinned-IP policy and no ambient credentials."""

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
        self._policy = policy or DirectHttpsAcquisitionPolicy()
        self._resolver = resolver
        self._connection_factory = connection_factory
        self._clock = clock
        self._monotonic = monotonic
        self._partial_root.mkdir(parents=True, exist_ok=True)
        self._committed_root.mkdir(parents=True, exist_ok=True)

    def acquire(self, request: ReferenceAcquisitionRequest) -> ReferenceAcquisitionResult:
        try:
            acquired = self._acquire(request)
        except _AcquisitionFailure as failure:
            return ReferenceAcquisitionResult(
                None,
                (
                    ReferenceAcquisitionDiagnostic(
                        failure.code,
                        failure.message,
                        failure.retryable,
                    ),
                ),
            )
        except (OSError, ssl.SSLError, http.client.HTTPException) as error:
            return ReferenceAcquisitionResult(
                None,
                (
                    ReferenceAcquisitionDiagnostic(
                        ReferenceAcquisitionDiagnosticCode.TRANSPORT_FAILED,
                        f"reference transport failed: {error}",
                        True,
                    ),
                ),
            )
        return ReferenceAcquisitionResult(acquired)

    def _acquire(self, request: ReferenceAcquisitionRequest) -> AcquiredReferenceMedia:
        original_url = request.url.strip()
        current_url = original_url
        deadline = self._monotonic() + self._policy.total_timeout_seconds
        redirects = 0

        while True:
            if self._monotonic() > deadline:
                raise _AcquisitionFailure(
                    ReferenceAcquisitionDiagnosticCode.TIME_LIMIT_EXCEEDED,
                    "reference acquisition exceeded the configured total time limit",
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
            response: _ResponseLike | None = None
            try:
                connection.request(
                    "GET",
                    _request_target(current_url),
                    headers={
                        "Accept": "video/*,application/octet-stream;q=0.8,*/*;q=0.1",
                        "Accept-Encoding": "identity",
                        "Connection": "close",
                        "User-Agent": "video-editing-agent/reference-acquisition-r0.12",
                    },
                )
                response = connection.getresponse()
                if response.status in _REDIRECT_STATUSES:
                    location = response.getheader("Location")
                    if location is None or not location.strip():
                        raise _AcquisitionFailure(
                            ReferenceAcquisitionDiagnosticCode.REDIRECT_REJECTED,
                            "reference redirect omitted a Location target",
                        )
                    if redirects >= self._policy.max_redirects:
                        raise _AcquisitionFailure(
                            ReferenceAcquisitionDiagnosticCode.REDIRECT_REJECTED,
                            "reference acquisition exceeded the redirect limit",
                        )
                    next_url = urljoin(current_url, location.strip())
                    self._validate_url_shape(next_url, redirect=True)
                    current_url = next_url
                    redirects += 1
                    continue
                if response.status in {401, 403}:
                    raise _AcquisitionFailure(
                        ReferenceAcquisitionDiagnosticCode.AUTHENTICATION_REQUIRED,
                        "reference requires authentication or provider authorization",
                    )
                if response.status == 404:
                    raise _AcquisitionFailure(
                        ReferenceAcquisitionDiagnosticCode.NOT_FOUND,
                        "reference media was not found",
                    )
                if response.status != 200:
                    raise _AcquisitionFailure(
                        ReferenceAcquisitionDiagnosticCode.TRANSPORT_FAILED,
                        f"reference server returned HTTP {response.status}",
                        retryable=response.status >= 500,
                    )

                content_type = _content_type_base(response.getheader("Content-Type"))
                if (
                    content_type is not None
                    and not content_type.startswith("video/")
                    and content_type not in _ALLOWED_GENERIC_CONTENT_TYPES
                ):
                    raise _AcquisitionFailure(
                        ReferenceAcquisitionDiagnosticCode.UNSUPPORTED_RESOURCE,
                        f"reference URL did not return direct video media ({content_type})",
                    )
                declared_length = self._declared_length(response)
                if declared_length is not None and declared_length > self._policy.max_bytes:
                    raise _AcquisitionFailure(
                        ReferenceAcquisitionDiagnosticCode.SIZE_LIMIT_EXCEEDED,
                        "reference media exceeds the configured byte limit",
                    )
                return self._commit_response(
                    response,
                    original_url=original_url,
                    final_url=current_url,
                    content_type=content_type,
                    deadline=deadline,
                )
            except (socket.timeout, TimeoutError) as error:
                raise _AcquisitionFailure(
                    ReferenceAcquisitionDiagnosticCode.TIME_LIMIT_EXCEEDED,
                    f"reference network operation timed out: {error}",
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
                ReferenceAcquisitionDiagnosticCode.REDIRECT_REJECTED
                if redirect
                else ReferenceAcquisitionDiagnosticCode.INVALID_URL,
                "reference URL contains an invalid port",
            ) from error
        if port <= 0:
            raise _AcquisitionFailure(
                ReferenceAcquisitionDiagnosticCode.REDIRECT_REJECTED
                if redirect
                else ReferenceAcquisitionDiagnosticCode.INVALID_URL,
                "reference URL contains an invalid port",
            )
        try:
            addresses = self._resolver(hostname, port)
        except OSError as error:
            raise _AcquisitionFailure(
                ReferenceAcquisitionDiagnosticCode.TRANSPORT_FAILED,
                f"reference hostname resolution failed: {error}",
                retryable=True,
            ) from error
        public = tuple(address for address in addresses if _public_address(address))
        if not public:
            raise _AcquisitionFailure(
                ReferenceAcquisitionDiagnosticCode.REDIRECT_REJECTED
                if redirect
                else ReferenceAcquisitionDiagnosticCode.NETWORK_TARGET_REJECTED,
                "reference URL does not resolve to an allowed public network address",
            )
        return hostname, port, public[0]

    @staticmethod
    def _validate_url_shape(url: str, *, redirect: bool) -> SplitResult:
        try:
            parts = urlsplit(url)
        except ValueError as error:
            raise _AcquisitionFailure(
                ReferenceAcquisitionDiagnosticCode.REDIRECT_REJECTED
                if redirect
                else ReferenceAcquisitionDiagnosticCode.INVALID_URL,
                "reference URL could not be parsed",
            ) from error
        if parts.scheme.casefold() != "https":
            raise _AcquisitionFailure(
                ReferenceAcquisitionDiagnosticCode.REDIRECT_REJECTED
                if redirect
                else ReferenceAcquisitionDiagnosticCode.UNSUPPORTED_SCHEME,
                "Stage-A reference acquisition supports HTTPS only",
            )
        if parts.username is not None or parts.password is not None:
            raise _AcquisitionFailure(
                ReferenceAcquisitionDiagnosticCode.REDIRECT_REJECTED
                if redirect
                else ReferenceAcquisitionDiagnosticCode.CREDENTIALS_NOT_ALLOWED,
                "embedded URL credentials are not allowed for reference acquisition",
            )
        if parts.hostname is None or not parts.hostname.strip():
            raise _AcquisitionFailure(
                ReferenceAcquisitionDiagnosticCode.REDIRECT_REJECTED
                if redirect
                else ReferenceAcquisitionDiagnosticCode.INVALID_URL,
                "reference URL requires a hostname",
            )
        return parts

    @staticmethod
    def _declared_length(response: _ResponseLike) -> int | None:
        raw = response.getheader("Content-Length")
        if raw is None:
            return None
        try:
            value = int(raw)
        except ValueError:
            return None
        return value if value >= 0 else None

    def _commit_response(
        self,
        response: _ResponseLike,
        *,
        original_url: str,
        final_url: str,
        content_type: str | None,
        deadline: float,
    ) -> AcquiredReferenceMedia:
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=self._partial_root,
                prefix=".reference-",
                suffix=".part",
                delete=False,
            ) as stream:
                temporary_path = Path(stream.name)
                digest = hashlib.sha256()
                byte_size = 0
                while True:
                    if self._monotonic() > deadline:
                        raise _AcquisitionFailure(
                            ReferenceAcquisitionDiagnosticCode.TIME_LIMIT_EXCEEDED,
                            "reference acquisition exceeded the configured total time limit",
                            retryable=True,
                        )
                    chunk = response.read(_CHUNK_SIZE)
                    if not chunk:
                        break
                    byte_size += len(chunk)
                    if byte_size > self._policy.max_bytes:
                        raise _AcquisitionFailure(
                            ReferenceAcquisitionDiagnosticCode.SIZE_LIMIT_EXCEEDED,
                            "reference media exceeds the configured byte limit",
                        )
                    digest.update(chunk)
                    stream.write(chunk)
                stream.flush()
                os.fsync(stream.fileno())

            digest_hex = digest.hexdigest()
            destination = self._committed_root / digest_hex[:2] / f"{digest_hex}.media"
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                if (
                    destination.stat().st_size != byte_size
                    or _file_sha256(destination) != digest_hex
                ):
                    raise _AcquisitionFailure(
                        ReferenceAcquisitionDiagnosticCode.INTEGRITY_FAILED,
                        "existing reference media failed content-address integrity validation",
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
                        ReferenceAcquisitionDiagnosticCode.INTEGRITY_FAILED,
                        "committed reference media failed integrity validation",
                    )
            return AcquiredReferenceMedia(
                local_path=destination.resolve(),
                original_url=original_url,
                final_url=final_url,
                provider="direct_https",
                provider_item_id=None,
                retrieved_at=self._clock(),
                content_hash=f"sha256:{digest_hex}",
                byte_size=byte_size,
                content_type=content_type,
            )
        except _AcquisitionFailure as failure:
            self._cleanup_partial(temporary_path, failure)
            raise
        except OSError as error:
            failure = _AcquisitionFailure(
                ReferenceAcquisitionDiagnosticCode.TRANSPORT_FAILED,
                f"reference media write failed: {error}",
                retryable=True,
            )
            self._cleanup_partial(temporary_path, failure)
            raise failure from error

    @staticmethod
    def _cleanup_partial(path: Path | None, failure: _AcquisitionFailure) -> None:
        if path is None or not path.exists():
            return
        try:
            path.unlink()
        except OSError as cleanup_error:
            raise _AcquisitionFailure(
                ReferenceAcquisitionDiagnosticCode.CLEANUP_FAILED,
                f"{failure.message}; partial cleanup also failed: {cleanup_error}",
            ) from failure
