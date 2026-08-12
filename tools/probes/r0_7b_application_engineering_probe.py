from __future__ import annotations

import json
import subprocess
import sys


def main() -> None:
    targets = (
        "tests/integration/test_r0_7b_preproduction_path.py",
        "tests/unit/test_project_workspace_cli.py",
        "tests/unit/test_temporal_evidence_persistence.py",
        "tests/unit/test_coverage_service.py",
        "tests/unit/test_sqlite_repositories.py",
    )
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *targets],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    evidence = {
        "probe": "r0.7b-application-engineering",
        "classification": (
            "engineering_complete" if completed.returncode == 0 else "engineering_failure"
        ),
        "exit_code": completed.returncode,
        "test_targets": list(targets),
        "preproduction_lifecycle": completed.returncode == 0,
        "bounded_semantic_repair": completed.returncode == 0,
        "revision_lock_persistence": completed.returncode == 0,
        "media_repository_lifecycle": completed.returncode == 0,
        "coverage_reshoot": completed.returncode == 0,
        "temporal_persistence": completed.returncode == 0,
        "external_provider_invoked": False,
        "visual_fallback": "reshoot_only",
        "test_summary": completed.stdout.strip().splitlines()[-1] if completed.stdout else "",
    }
    print(json.dumps(evidence, ensure_ascii=False, sort_keys=True))
    if completed.returncode != 0:
        print(completed.stdout, file=sys.stderr)
        print(completed.stderr, file=sys.stderr)
        raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
