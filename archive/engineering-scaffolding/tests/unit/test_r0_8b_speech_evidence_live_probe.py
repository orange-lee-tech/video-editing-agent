from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))
probe = importlib.import_module("tools.probes.r0_8b_speech_evidence_live")


def test_live_probe_refuses_to_overwrite_existing_database(tmp_path: Path) -> None:
    database_path = tmp_path / "existing.sqlite3"
    database_path.write_text("do not delete", encoding="utf-8")

    with pytest.raises(FileExistsError, match="choose a fresh path"):
        probe._require_fresh_database_path(database_path)

    assert database_path.read_text(encoding="utf-8") == "do not delete"
