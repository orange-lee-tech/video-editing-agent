import json
from datetime import UTC, datetime

from video_editing_agent.domain.asset.model import Asset, AssetProvenance
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.storage.repositories.record_codec import decode_asset, encode_asset

NOW = datetime(2026, 8, 11, 2, 0, tzinfo=UTC)


def make_asset(envelope: EntityEnvelope) -> Asset:
    return Asset(
        envelope=envelope,
        media_kind="video",
        origin="local",
        storage_ref="file:///tmp/example.mp4",
        content_hash="sha256:" + "1" * 64,
        byte_size=100,
        provenance=AssetProvenance(origin_type="local"),
        imported_at=NOW,
    )


def test_record_codec_round_trips_entity_derivation_lineage() -> None:
    source_ref = EntityRevisionRef("ast_source", 2)
    original = make_asset(
        EntityEnvelope(
            id="ast_derived",
            revision=1,
            schema_version="0.1.1",
            status=EntityStatus.VALID,
            created_at=NOW,
            created_by="test",
            derived_from=(source_ref,),
        )
    )

    loaded = decode_asset(encode_asset(original))

    assert loaded.envelope.derived_from == (source_ref,)


def test_record_codec_reads_legacy_envelope_without_derived_from() -> None:
    original = make_asset(
        EntityEnvelope(
            id="ast_legacy",
            revision=1,
            schema_version="0.1.1",
            status=EntityStatus.VALID,
            created_at=NOW,
            created_by="test",
        )
    )
    payload = json.loads(encode_asset(original))
    del payload["envelope"]["derived_from"]

    loaded = decode_asset(json.dumps(payload))

    assert loaded.envelope.derived_from == ()
