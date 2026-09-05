from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from urllib.parse import urljoin
from urllib.request import Request

DEFAULT_UPDATE_MANIFEST_URL = (
    "https://orange-lee-tech.github.io/homepages/video-editing-agent/stable/latest.json"
)
_MAX_REDIRECTS = 5


@dataclass(frozen=True, slots=True)
class UpdateOriginPolicy:
    pages_host: str = "orange-lee-tech.github.io"
    pages_prefix: str = "/homepages/video-editing-agent/"
    github_host: str = "github.com"
    github_prefix: str = "/orange-lee-tech/video-editing-agent/"
    release_cdn_hosts: frozenset[str] = frozenset(
        {
            "objects.githubusercontent.com",
            "release-assets.githubusercontent.com",
            "github-releases.githubusercontent.com",
        }
    )


DEFAULT_UPDATE_ORIGIN_POLICY = UpdateOriginPolicy()


def assert_allowed_update_url(
    url: str,
    *,
    role: str,
    policy: UpdateOriginPolicy = DEFAULT_UPDATE_ORIGIN_POLICY,
    allow_release_cdn: bool = False,
) -> None:
    try:
        parts = urllib.parse.urlsplit(url)
    except ValueError as exc:
        raise ValueError("update URL could not be parsed") from exc
    if parts.scheme.casefold() != "https":
        raise ValueError("update URLs must use HTTPS")
    if parts.username is not None or parts.password is not None:
        raise ValueError("update URLs must not contain embedded credentials")
    hostname = (parts.hostname or "").casefold()
    if not hostname:
        raise ValueError("update URLs require a hostname")
    if parts.port not in {None, 443}:
        raise ValueError("update URLs must use port 443")
    path = parts.path or "/"
    if ".." in path.split("/"):
        raise ValueError("update URL path must not contain parent segments")
    if hostname == policy.pages_host:
        if not path.startswith(policy.pages_prefix):
            raise ValueError("GitHub Pages update URL is outside the product path")
        return
    if hostname == policy.github_host:
        if role == "component":
            download_prefix = f"{policy.github_prefix.rstrip('/')}/releases/download/"
            if not path.startswith(download_prefix):
                raise ValueError("component patch URL must be a GitHub Release asset")
        elif not path.startswith(policy.github_prefix):
            raise ValueError("GitHub update URL is outside the product repository")
        return
    if allow_release_cdn and hostname in policy.release_cdn_hosts:
        return
    raise ValueError(f"update URL host is not an allowed release origin: {hostname}")


class _AllowlistedHTTPSRedirectHandler(urllib.request.HTTPRedirectHandler):
    max_redirections = _MAX_REDIRECTS

    def __init__(self, policy: UpdateOriginPolicy) -> None:
        super().__init__()
        self._policy = policy

    def redirect_request(
        self,
        req: Request,
        fp: object,
        code: int,
        msg: str,
        headers: object,
        newurl: str,
    ) -> Request | None:
        if code not in {301, 302, 303, 307, 308}:
            return None
        absolute = urljoin(req.full_url, newurl)
        assert_allowed_update_url(
            absolute,
            role="redirect",
            policy=self._policy,
            allow_release_cdn=True,
        )
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is None:
            return None
        assert_allowed_update_url(
            redirected.full_url,
            role="redirect",
            policy=self._policy,
            allow_release_cdn=True,
        )
        return redirected


def fetch_https_bytes(
    url: str,
    *,
    timeout_seconds: float,
    max_bytes: int,
    user_agent: str,
    role: str,
    policy: UpdateOriginPolicy = DEFAULT_UPDATE_ORIGIN_POLICY,
) -> bytes:
    assert_allowed_update_url(url, role=role, policy=policy)
    request = Request(url, headers={"User-Agent": user_agent})
    https = urllib.request.HTTPSHandler()
    opener = urllib.request.build_opener(https, _AllowlistedHTTPSRedirectHandler(policy))
    received = bytearray()
    try:
        with opener.open(request, timeout=timeout_seconds) as response:
            while True:
                remaining = max_bytes + 1 - len(received)
                if remaining <= 0:
                    raise ValueError("downloaded update payload exceeds the declared size")
                chunk = response.read(min(1024 * 1024, remaining))
                if not chunk:
                    break
                received.extend(chunk)
    except urllib.error.URLError as exc:
        raise ValueError(f"update download failed: {exc}") from exc
    if len(received) > max_bytes:
        raise ValueError("downloaded update payload exceeds the declared size")
    return bytes(received)
