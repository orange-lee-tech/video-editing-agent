from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from video_editing_agent.application.ports.audio_acquisition import AudioAcquisitionRequest
from video_editing_agent.application.ports.audio_material_provider import MusicDiscoveryQuery
from video_editing_agent.domain.asset.model import AssetProvenance
from video_editing_agent.domain.asset.policy import AssetOrigin, AssetUsageRole
from video_editing_agent.domain.asset.rights import RightsEligibility
from video_editing_agent.media.ingest.ffprobe import FfprobeMediaProbe
from video_editing_agent.media.ingest.service import AssetIngestService
from video_editing_agent.media.ingest.source import LocalMediaSource
from video_editing_agent.providers.audio.openverse import OpenverseWikimediaAudioProvider
from video_editing_agent.providers.audio.wikimedia import WikimediaAudioRightsVerifier
from video_editing_agent.providers.audio.wikimedia_acquisition import WikimediaAudioAcquirer
from video_editing_agent.storage.artifact.local_store import LocalArtifactStore

QUERIES = (
    "piano instrumental",
    "acoustic instrumental music",
    "classical instrumental music",
)
_OPENVERSE_AUDIO_ENDPOINT = "https://api.openverse.org/v1/audio/"


def _emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))


def _raw_openverse_diagnostic(query_text: str) -> list[dict[str, object]]:
    variants: tuple[tuple[str, str | None], ...] = (
        ("source_only", None),
        ("commercial", "commercial"),
        ("modification", "modification"),
        ("commercial_and_modification", "commercial,modification"),
    )
    diagnostics: list[dict[str, object]] = []
    for label, license_type in variants:
        parameters = {
            "q": query_text,
            "source": "wikimedia_audio",
            "page_size": "5",
            "filter_dead": "true",
        }
        if license_type is not None:
            parameters["license_type"] = license_type
        url = f"{_OPENVERSE_AUDIO_ENDPOINT}?{urlencode(parameters)}"
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "video-editing-agent/public-music-r0.12-probe",
            },
            method="GET",
        )
        diagnostic: dict[str, object] = {
            "variant": label,
            "license_type": license_type,
        }
        try:
            with urlopen(request, timeout=30.0) as response:  # noqa: S310 - fixed Openverse endpoint
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as error:  # noqa: BLE001 - live probe preserves provider failure evidence
            diagnostic["error"] = f"{type(error).__name__}: {error}"
            diagnostics.append(diagnostic)
            continue

        if not isinstance(payload, dict):
            diagnostic["error"] = "Openverse response root was not an object"
            diagnostics.append(diagnostic)
            continue
        raw_results = payload.get("results")
        if not isinstance(raw_results, list):
            diagnostic["error"] = "Openverse response omitted results list"
            diagnostics.append(diagnostic)
            continue

        diagnostic["raw_result_count"] = len(raw_results)
        samples: list[dict[str, object]] = []
        for raw in raw_results[:3]:
            if not isinstance(raw, dict):
                continue
            samples.append(
                {
                    key: raw.get(key)
                    for key in (
                        "id",
                        "source",
                        "title",
                        "foreign_landing_url",
                        "foreign_identifier",
                        "license",
                        "license_url",
                        "filetype",
                    )
                }
            )
        diagnostic["samples"] = samples
        diagnostics.append(diagnostic)
    return diagnostics


def main() -> int:
    evidence: dict[str, object] = {
        "probe": "R0.12 public music provider live",
        "result": "FAIL",
        "queries": [],
        "acquisition_attempts": 0,
        "openverse_raw_diagnostic": _raw_openverse_diagnostic(QUERIES[0]),
    }

    with tempfile.TemporaryDirectory(prefix="r0-12-public-music-") as temp_dir:
        root = Path(temp_dir).resolve()
        artifacts = LocalArtifactStore(root / "artifacts")
        provider = OpenverseWikimediaAudioProvider(page_size=20)
        verifier = WikimediaAudioRightsVerifier(artifacts)
        selected = None

        for query_text in QUERIES:
            query_evidence: dict[str, object] = {
                "query": query_text,
                "candidate_count": 0,
                "verification_attempts": [],
            }
            cast_queries = evidence["queries"]
            assert isinstance(cast_queries, list)
            cast_queries.append(query_evidence)

            try:
                candidates = provider.search_music(MusicDiscoveryQuery(query_text))
            except Exception as error:  # noqa: BLE001 - live probe preserves provider failure evidence
                query_evidence["discovery_error"] = f"{type(error).__name__}: {error}"
                continue

            query_evidence["candidate_count"] = len(candidates)
            attempts = query_evidence["verification_attempts"]
            assert isinstance(attempts, list)

            for candidate in candidates:
                attempt: dict[str, object] = {
                    "provider_item_id": candidate.provider_item_id,
                    "title": candidate.title,
                    "discovery_rights": candidate.rights_eligibility.value,
                    "generated_audio_state": candidate.is_generated_audio,
                }
                attempts.append(attempt)
                try:
                    verification = verifier.verify(candidate.provider_item_id)
                except Exception as error:  # noqa: BLE001 - live probe preserves source failure evidence
                    attempt["verification_error"] = f"{type(error).__name__}: {error}"
                    continue

                if not verification.is_verified or verification.verified is None:
                    attempt["verified"] = False
                    attempt["diagnostics"] = [
                        {"code": diagnostic.code.value, "message": diagnostic.message}
                        for diagnostic in verification.diagnostics
                    ]
                    continue

                verified = verification.verified
                attempt.update(
                    {
                        "verified": True,
                        "license_identifier": verified.license_identifier,
                        "rights_eligibility": verified.snapshot.eligibility.value,
                        "source_page": verified.source_page,
                        "source_url": verified.source_url,
                        "source_sha1": verified.source_sha1,
                        "source_byte_size": verified.byte_size,
                        "source_mime_type": verified.mime_type,
                        "rights_artifact_ref": verified.rights_artifact_ref,
                        "rights_evidence_refs": list(verified.snapshot.evidence_artifact_refs),
                    }
                )
                if verified.snapshot.eligibility is not RightsEligibility.ELIGIBLE:
                    attempt["automatic_selection"] = "skipped_non_eligible"
                    continue
                attempt["automatic_selection"] = "eligible"
                selected = verified
                break

            if selected is not None:
                break

        if selected is None:
            evidence["failure"] = (
                "no Openverse/Wikimedia candidate cleared the automatic ELIGIBLE rights gate"
            )
            _emit(evidence)
            return 1

        evidence["selected"] = {
            "provider_item_id": selected.provider_item_id,
            "source_page": selected.source_page,
            "source_url": selected.source_url,
            "source_sha1": selected.source_sha1,
            "source_byte_size": selected.byte_size,
            "source_mime_type": selected.mime_type,
            "license_identifier": selected.license_identifier,
            "license_url": selected.license_url,
            "rights_eligibility": selected.snapshot.eligibility.value,
            "rights_artifact_ref": selected.rights_artifact_ref,
            "rights_evidence_refs": list(selected.snapshot.evidence_artifact_refs),
            "creator": selected.creator,
            "attribution_required": selected.attribution_required,
            "attribution_text": selected.attribution_text,
        }

        acquisition_request = AudioAcquisitionRequest(
            provider="wikimedia_commons",
            provider_item_id=selected.provider_item_id,
            approved_source_url=selected.source_url,
            source_page=selected.source_page,
            license_snapshot_ref=selected.rights_artifact_ref,
            rights_eligibility=selected.snapshot.eligibility,
            expected_source_sha1=selected.source_sha1,
            expected_byte_size=selected.byte_size,
            expected_content_type=selected.mime_type,
        )
        evidence["acquisition_attempts"] = 1
        acquisition = WikimediaAudioAcquirer(root / "provider_audio").acquire(acquisition_request)
        if not acquisition.is_acquired or acquisition.acquired is None:
            evidence["failure"] = "verified Wikimedia candidate failed acquisition"
            evidence["acquisition_diagnostics"] = [
                {
                    "code": diagnostic.code.value,
                    "message": diagnostic.message,
                    "retryable": diagnostic.retryable,
                }
                for diagnostic in acquisition.diagnostics
            ]
            _emit(evidence)
            return 1

        acquired = acquisition.acquired
        evidence["acquired"] = {
            "provider": acquired.provider,
            "provider_item_id": acquired.provider_item_id,
            "source_page": acquired.source_page,
            "final_source_url": acquired.final_source_url,
            "byte_size": acquired.byte_size,
            "local_sha256": acquired.local_sha256,
            "source_sha1": acquired.source_sha1,
            "content_type": acquired.content_type,
            "license_snapshot_ref": acquired.license_snapshot_ref,
        }

        probe = FfprobeMediaProbe()
        technical = probe.probe(acquired.local_path)
        evidence["ffprobe"] = {
            "media_kind": technical.media_kind,
            "duration_seconds": (
                None
                if technical.duration is None
                else technical.duration.to_decimal_seconds_string()
            ),
            "codec": technical.codec,
            "audio_channels": technical.audio_channels,
            "sample_rate_hz": technical.sample_rate_hz,
        }
        if technical.media_kind != "audio":
            evidence["failure"] = f"ffprobe classified acquired media as {technical.media_kind!r}"
            _emit(evidence)
            return 1

        asset = AssetIngestService(probe).ingest(
            LocalMediaSource(
                acquired.local_path,
                AssetOrigin.PROVIDER_ACQUIRED_AUDIO,
                AssetProvenance(
                    origin_type=AssetOrigin.PROVIDER_ACQUIRED_AUDIO,
                    provider=acquired.provider,
                    provider_asset_id=acquired.provider_item_id,
                    source_page=acquired.source_page,
                    creator=selected.creator,
                    retrieved_at=acquired.acquired_at,
                    license_information=selected.license_identifier,
                    attribution=selected.attribution_text,
                ),
                AssetUsageRole.MUSIC,
            ),
            created_by="r0.12-public-music-provider-probe",
        )
        evidence["asset"] = {
            "asset_id": asset.envelope.id,
            "media_kind": asset.media_kind,
            "origin": asset.origin,
            "usage_role": asset.usage_role.value,
            "content_hash": asset.content_hash,
            "byte_size": asset.byte_size,
            "codec": asset.codec,
            "audio_channels": asset.audio_channels,
            "sample_rate_hz": asset.sample_rate_hz,
            "provider": asset.provenance.provider,
            "provider_asset_id": asset.provenance.provider_asset_id,
            "source_page": asset.provenance.source_page,
            "license_information": asset.provenance.license_information,
            "attribution": asset.provenance.attribution,
        }

        if asset.origin != AssetOrigin.PROVIDER_ACQUIRED_AUDIO:
            evidence["failure"] = "Asset origin did not preserve provider acquisition authority"
            _emit(evidence)
            return 1
        if asset.usage_role is not AssetUsageRole.MUSIC:
            evidence["failure"] = "Asset usage role is not MUSIC"
            _emit(evidence)
            return 1
        if asset.content_hash != acquired.local_sha256:
            evidence["failure"] = "Asset content hash diverged from acquired local SHA-256"
            _emit(evidence)
            return 1

        evidence["result"] = "PASS"
        _emit(evidence)
        return 0


if __name__ == "__main__":
    sys.exit(main())
