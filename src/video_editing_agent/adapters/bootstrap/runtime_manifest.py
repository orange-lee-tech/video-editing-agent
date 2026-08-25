from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any

RUNTIME_MANIFEST_SCHEMA = "video-editing-agent/runtime-manifest/v1"
_COMPONENT_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_RELEASE_PARTS = {".git", ".private", ".tools", ".venv", "build", "dist"}


class RuntimeComponentKind(StrEnum):
    EXECUTABLE = "executable"
    MODEL = "model"
    RESOURCE = "resource"
    RUNTIME = "runtime"
    REMOTE_SERVICE = "remote-service"
    DEVELOPMENT_TOOL = "development-tool"


class RuntimeComponentClass(StrEnum):
    BUNDLED_REQUIRED = "bundled-required"
    BUNDLED_OPTIONAL = "bundled-optional"
    MANAGED_OPTIONAL = "managed-optional"
    REMOTE = "remote"
    DEVELOPMENT_ONLY = "development-only"


class InclusionPolicy(StrEnum):
    INCLUDE = "include"
    EXTERNAL = "external"
    EXCLUDE = "exclude"


class LicenseState(StrEnum):
    REVIEWED = "reviewed"
    EXTERNAL_REVIEW_REQUIRED = "external-review-required"
    NOT_APPLICABLE = "not-applicable"


class HashPolicy(StrEnum):
    EXACT = "exact"
    BUILD_GENERATED = "build-generated"
    NOT_APPLICABLE = "not-applicable"


@dataclass(frozen=True, slots=True)
class RuntimeComponent:
    component_id: str
    kind: RuntimeComponentKind
    classification: RuntimeComponentClass
    capability: str
    version: str
    location_policy: str
    provenance: str
    license_state: LicenseState
    inclusion: InclusionPolicy
    hash_policy: HashPolicy
    relative_path: PurePosixPath | None = None
    sha256: str | None = None
    notice_path: PurePosixPath | None = None
    platform: str = "any"
    architecture: str = "any"
    absence_fatal: bool = False

    def __post_init__(self) -> None:
        if _COMPONENT_ID.fullmatch(self.component_id) is None:
            raise ValueError(f"invalid runtime component id: {self.component_id!r}")
        for label, value in (
            ("capability", self.capability),
            ("version", self.version),
            ("location_policy", self.location_policy),
            ("provenance", self.provenance),
            ("platform", self.platform),
            ("architecture", self.architecture),
        ):
            if not value.strip():
                raise ValueError(f"component {label} must not be blank")
        if self.relative_path is not None:
            _validate_relative_path(self.relative_path)
            if (
                self.classification is not RuntimeComponentClass.DEVELOPMENT_ONLY
                and _FORBIDDEN_RELEASE_PARTS.intersection(self.relative_path.parts)
            ):
                raise ValueError("release component path contains developer-only content")
        if self.notice_path is not None:
            _validate_relative_path(self.notice_path)
        if self.inclusion is InclusionPolicy.INCLUDE and self.relative_path is None:
            raise ValueError("included component requires a relative_path")
        if self.classification is RuntimeComponentClass.BUNDLED_REQUIRED:
            if self.inclusion is not InclusionPolicy.INCLUDE:
                raise ValueError("bundled-required component must be included")
            if self.license_state is LicenseState.EXTERNAL_REVIEW_REQUIRED:
                raise ValueError("bundled-required component license must be reviewed")
        if self.hash_policy is HashPolicy.EXACT:
            if self.sha256 is None or _SHA256.fullmatch(self.sha256) is None:
                raise ValueError("exact component hash requires 64 lowercase hex sha256")
        elif self.sha256 is not None:
            raise ValueError("sha256 is allowed only with exact hash policy")
        if (
            self.classification
            in {
                RuntimeComponentClass.REMOTE,
                RuntimeComponentClass.DEVELOPMENT_ONLY,
            }
            and self.inclusion is not InclusionPolicy.EXCLUDE
        ):
            raise ValueError("remote/development-only components must be excluded")

    @property
    def required_in_artifact(self) -> bool:
        return self.inclusion is InclusionPolicy.INCLUDE


@dataclass(frozen=True, slots=True)
class RuntimeManifest:
    application_version: str
    components: tuple[RuntimeComponent, ...]
    schema: str = RUNTIME_MANIFEST_SCHEMA

    def __post_init__(self) -> None:
        if self.schema != RUNTIME_MANIFEST_SCHEMA:
            raise ValueError(f"unsupported runtime manifest schema: {self.schema!r}")
        if not self.application_version.strip():
            raise ValueError("application_version must not be blank")
        ids = tuple(item.component_id for item in self.components)
        if len(ids) != len(set(ids)):
            raise ValueError("runtime component ids must be unique")
        paths = tuple(
            str(item.relative_path)
            for item in self.components
            if item.inclusion is InclusionPolicy.INCLUDE and item.relative_path is not None
        )
        if len(paths) != len(set(paths)):
            raise ValueError("included runtime component paths must have unique ownership")

    def component(self, component_id: str) -> RuntimeComponent | None:
        return next((item for item in self.components if item.component_id == component_id), None)


def load_runtime_manifest(path: Path) -> RuntimeManifest:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"runtime manifest could not be loaded: {exc}") from exc
    return parse_runtime_manifest(payload)


def parse_runtime_manifest(payload: object) -> RuntimeManifest:
    root = _mapping(payload, "runtime manifest")
    _require_exact_keys(root, {"schema", "application_version", "components"}, "manifest")
    raw_components = root["components"]
    if not isinstance(raw_components, list):
        raise ValueError("manifest components must be a list")
    return RuntimeManifest(
        schema=_string(root["schema"], "schema"),
        application_version=_string(root["application_version"], "application_version"),
        components=tuple(_parse_component(item) for item in raw_components),
    )


def _parse_component(payload: object) -> RuntimeComponent:
    item = _mapping(payload, "runtime component")
    required = {
        "id",
        "kind",
        "classification",
        "capability",
        "version",
        "location_policy",
        "provenance",
        "license_state",
        "inclusion",
        "hash_policy",
        "platform",
        "architecture",
        "absence_fatal",
    }
    optional = {"path", "sha256", "notice_path"}
    if not required.issubset(item):
        raise ValueError(f"runtime component is missing keys: {sorted(required - item.keys())}")
    if not set(item).issubset(required | optional):
        raise ValueError(
            f"runtime component has unknown keys: {sorted(set(item) - required - optional)}"
        )
    absence_fatal = item["absence_fatal"]
    if not isinstance(absence_fatal, bool):
        raise ValueError("component absence_fatal must be a boolean")
    return RuntimeComponent(
        component_id=_string(item["id"], "component id"),
        kind=_enum(RuntimeComponentKind, item["kind"], "component kind"),
        classification=_enum(RuntimeComponentClass, item["classification"], "classification"),
        capability=_string(item["capability"], "capability"),
        version=_string(item["version"], "version"),
        location_policy=_string(item["location_policy"], "location_policy"),
        provenance=_string(item["provenance"], "provenance"),
        license_state=_enum(LicenseState, item["license_state"], "license_state"),
        inclusion=_enum(InclusionPolicy, item["inclusion"], "inclusion"),
        hash_policy=_enum(HashPolicy, item["hash_policy"], "hash_policy"),
        relative_path=_optional_path(item.get("path"), "path"),
        sha256=_optional_string(item.get("sha256"), "sha256"),
        notice_path=_optional_path(item.get("notice_path"), "notice_path"),
        platform=_string(item["platform"], "platform"),
        architecture=_string(item["architecture"], "architecture"),
        absence_fatal=absence_fatal,
    )


def _validate_relative_path(path: PurePosixPath) -> None:
    value = str(path)
    if not value or value == "." or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"component path must be a bounded relative path: {value!r}")
    if "\\" in value or ":" in value:
        raise ValueError(f"component path must use portable relative syntax: {value!r}")


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{label} must be an object with string keys")
    return value


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _optional_string(value: object, label: str) -> str | None:
    return None if value is None else _string(value, label)


def _optional_path(value: object, label: str) -> PurePosixPath | None:
    return None if value is None else PurePosixPath(_string(value, label))


def _enum[T: StrEnum](enum_type: type[T], value: object, label: str) -> T:
    try:
        return enum_type(_string(value, label))
    except ValueError as exc:
        raise ValueError(f"unsupported {label}: {value!r}") from exc


def _require_exact_keys(value: dict[str, Any], keys: set[str], label: str) -> None:
    if set(value) != keys:
        raise ValueError(f"{label} keys must be exactly {sorted(keys)}; got {sorted(value)}")
