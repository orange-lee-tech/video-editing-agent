import pytest

from video_editing_agent.domain.common.entity import EntityRevisionRef


def test_entity_revision_ref_accepts_valid_revision() -> None:
    ref = EntityRevisionRef(entity_id="scp_test", revision=1)

    assert ref.entity_id == "scp_test"
    assert ref.revision == 1


def test_entity_revision_ref_rejects_zero_revision() -> None:
    with pytest.raises(ValueError):
        EntityRevisionRef(entity_id="scp_test", revision=0)


def test_entity_revision_ref_rejects_empty_id() -> None:
    with pytest.raises(ValueError):
        EntityRevisionRef(entity_id="", revision=1)
