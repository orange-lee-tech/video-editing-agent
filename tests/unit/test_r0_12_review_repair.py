from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from video_editing_agent.application.ports.executor import DeterministicToolInvocation
from video_editing_agent.application.ports.rendered_media_qc import (
    RenderedMediaQcCode,
    RenderedMediaQcFinding,
    RenderedMediaQcResult,
)
from video_editing_agent.application.ports.renderer import (
    OutputSpec,
    RenderArtifact,
    RenderDiagnostic,
    RenderDiagnosticCode,
    RenderResult,
)
from video_editing_agent.application.use_cases.review_runtime import (
    MAX_SAME_EDL_REPAIR_ATTEMPTS,
    ReviewApplicationRuntime,
    ReviewRequest,
)
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.review.model import (
    ReviewCorrectionRoute,
    ReviewDisposition,
    ReviewStage,
)


class FakeRenderedMediaQc:
    def __init__(self, result: RenderedMediaQcResult) -> None:
        self.result = result
        self.calls: list[Path] = []

    def inspect(self, path: Path) -> RenderedMediaQcResult:
        self.calls.append(path)
        return self.result


def _clock() -> datetime:
    return datetime(2026, 8, 17, 12, 0, tzinfo=timezone.utc)


def _invocation(identity: str) -> DeterministicToolInvocation:
    return DeterministicToolInvocation(identity, "fixture-tool", ())


def _artifact(tmp_path: Path, edl_ref: EntityRevisionRef) -> RenderArtifact:
    path = tmp_path / "final.mp4"
    path.write_bytes(b"rendered")
    return RenderArtifact(
        path,
        edl_ref,
        OutputSpec(path, 1280, 720, 30),
        _invocation("render"),
        _invocation("verify"),
    )


def _qc(
    path: Path,
    *,
    audio_stream_present: bool | None = True,
    silent_fraction: float | None = 0.1,
    clipped_samples: int | None = 0,
    codes: tuple[RenderedMediaQcCode, ...] = (),
) -> RenderedMediaQcResult:
    return RenderedMediaQcResult(
        path,
        audio_stream_present,
        -1.0 if audio_stream_present else None,
        -18.0 if audio_stream_present else None,
        silent_fraction,
        clipped_samples,
        tuple(RenderedMediaQcFinding(code, code.value) for code in codes),
        (),
    )


def _runtime(qc: FakeRenderedMediaQc) -> ReviewApplicationRuntime:
    return ReviewApplicationRuntime(qc, clock=_clock)


def test_matching_artifact_and_clean_media_pass(tmp_path: Path) -> None:
    edl_ref = EntityRevisionRef("edl-clean", 3)
    artifact = _artifact(tmp_path, edl_ref)
    qc = FakeRenderedMediaQc(_qc(artifact.path))

    verdict = _runtime(qc).review(
        ReviewRequest(edl_ref, RenderResult(artifact, ()), requires_audible_output=True)
    )

    assert verdict.disposition is ReviewDisposition.PASS
    assert verdict.correction_route is ReviewCorrectionRoute.NONE
    assert verdict.report.passed is True
    assert verdict.report.stage is ReviewStage.FINAL_TECHNICAL_QC
    assert verdict.report.target_ref == edl_ref
    assert qc.calls == [artifact.path]


def test_artifact_edl_revision_mismatch_blocks_before_qc(tmp_path: Path) -> None:
    requested = EntityRevisionRef("edl", 2)
    artifact = _artifact(tmp_path, EntityRevisionRef("edl", 1))
    qc = FakeRenderedMediaQc(_qc(artifact.path))

    verdict = _runtime(qc).review(
        ReviewRequest(requested, RenderResult(artifact, ()), requires_audible_output=True)
    )

    assert verdict.disposition is ReviewDisposition.BLOCKED
    assert verdict.correction_route is ReviewCorrectionRoute.ESCALATE_OWNER
    assert verdict.report.findings[0].finding_id.endswith("artifact-edl-provenance-mismatch")
    assert qc.calls == []


def test_missing_or_uninspectable_output_is_blocked(tmp_path: Path) -> None:
    edl_ref = EntityRevisionRef("edl-missing", 1)
    artifact = _artifact(tmp_path, edl_ref)
    qc = FakeRenderedMediaQc(
        _qc(
            artifact.path,
            audio_stream_present=None,
            silent_fraction=None,
            clipped_samples=None,
            codes=(RenderedMediaQcCode.OUTPUT_MISSING,),
        )
    )

    verdict = _runtime(qc).review(
        ReviewRequest(edl_ref, RenderResult(artifact, ()), requires_audible_output=True)
    )

    assert verdict.disposition is ReviewDisposition.BLOCKED
    assert verdict.correction_route is ReviewCorrectionRoute.ESCALATE_OWNER
    assert verdict.report.findings[0].affected_owner == "RenderedMediaQc/Environment"


def test_intentional_silence_accepts_no_audio_stream(tmp_path: Path) -> None:
    edl_ref = EntityRevisionRef("edl-silent", 1)
    artifact = _artifact(tmp_path, edl_ref)
    qc = FakeRenderedMediaQc(
        _qc(
            artifact.path,
            audio_stream_present=False,
            silent_fraction=None,
            clipped_samples=None,
            codes=(RenderedMediaQcCode.NO_AUDIO_STREAM,),
        )
    )

    verdict = _runtime(qc).review(
        ReviewRequest(edl_ref, RenderResult(artifact, ()), requires_audible_output=False)
    )

    assert verdict.disposition is ReviewDisposition.PASS
    assert verdict.correction_route is ReviewCorrectionRoute.NONE


def test_audible_intent_without_audio_stream_blocks_as_inconsistent(tmp_path: Path) -> None:
    edl_ref = EntityRevisionRef("edl-audible", 1)
    artifact = _artifact(tmp_path, edl_ref)
    qc = FakeRenderedMediaQc(
        _qc(
            artifact.path,
            audio_stream_present=False,
            silent_fraction=None,
            clipped_samples=None,
            codes=(RenderedMediaQcCode.NO_AUDIO_STREAM,),
        )
    )

    verdict = _runtime(qc).review(
        ReviewRequest(edl_ref, RenderResult(artifact, ()), requires_audible_output=True)
    )

    assert verdict.disposition is ReviewDisposition.BLOCKED
    assert verdict.report.findings[0].affected_owner == "AudioEditorialService/Application"


def test_unexpected_mostly_silent_output_routes_to_audio_editorial(tmp_path: Path) -> None:
    edl_ref = EntityRevisionRef("edl-mostly-silent", 1)
    artifact = _artifact(tmp_path, edl_ref)
    qc = FakeRenderedMediaQc(
        _qc(
            artifact.path,
            silent_fraction=0.99,
            codes=(RenderedMediaQcCode.MOSTLY_SILENT,),
        )
    )

    verdict = _runtime(qc).review(
        ReviewRequest(edl_ref, RenderResult(artifact, ()), requires_audible_output=True)
    )

    assert verdict.disposition is ReviewDisposition.CORRECTION_REQUIRED
    assert verdict.correction_route is ReviewCorrectionRoute.RETURN_TO_AUDIO_EDITORIAL
    assert verdict.report.findings[0].affected_owner == "AudioEditorialService"


def test_clipping_routes_to_audio_editorial_without_mutating_render(tmp_path: Path) -> None:
    edl_ref = EntityRevisionRef("edl-clipping", 1)
    artifact = _artifact(tmp_path, edl_ref)
    qc = FakeRenderedMediaQc(
        _qc(
            artifact.path,
            clipped_samples=42,
            codes=(RenderedMediaQcCode.CLIPPING,),
        )
    )
    original_bytes = artifact.path.read_bytes()

    verdict = _runtime(qc).review(
        ReviewRequest(edl_ref, RenderResult(artifact, ()), requires_audible_output=True)
    )

    assert verdict.disposition is ReviewDisposition.CORRECTION_REQUIRED
    assert verdict.correction_route is ReviewCorrectionRoute.RETURN_TO_AUDIO_EDITORIAL
    assert artifact.path.read_bytes() == original_bytes


def test_inspection_failure_stays_typed_and_never_becomes_pass(tmp_path: Path) -> None:
    edl_ref = EntityRevisionRef("edl-inspection-fail", 1)
    artifact = _artifact(tmp_path, edl_ref)
    qc = FakeRenderedMediaQc(
        _qc(
            artifact.path,
            audio_stream_present=None,
            silent_fraction=None,
            clipped_samples=None,
            codes=(RenderedMediaQcCode.INSPECTION_FAILED,),
        )
    )

    verdict = _runtime(qc).review(
        ReviewRequest(edl_ref, RenderResult(artifact, ()), requires_audible_output=True)
    )

    assert verdict.disposition is ReviewDisposition.BLOCKED
    assert verdict.correction_route is ReviewCorrectionRoute.ESCALATE_OWNER


def test_execution_failure_can_request_one_same_edl_rerender() -> None:
    edl_ref = EntityRevisionRef("edl-retry", 4)
    diagnostic = RenderDiagnostic(RenderDiagnosticCode.EXECUTION_FAILED, "ffmpeg process failed")
    qc = FakeRenderedMediaQc(_qc(Path("unused.mp4")))

    verdict = _runtime(qc).review(
        ReviewRequest(
            edl_ref,
            RenderResult(None, (diagnostic,)),
            requires_audible_output=True,
            repair_attempt=0,
        )
    )

    assert verdict.disposition is ReviewDisposition.CORRECTION_REQUIRED
    assert verdict.correction_route is ReviewCorrectionRoute.RERENDER_SAME_EDL
    assert verdict.report.target_ref == edl_ref
    assert qc.calls == []


def test_same_edl_retry_bound_is_enforced() -> None:
    edl_ref = EntityRevisionRef("edl-retry", 4)
    diagnostic = RenderDiagnostic(
        RenderDiagnosticCode.OUTPUT_VERIFICATION_FAILED,
        "verification failed",
    )
    qc = FakeRenderedMediaQc(_qc(Path("unused.mp4")))

    verdict = _runtime(qc).review(
        ReviewRequest(
            edl_ref,
            RenderResult(None, (diagnostic,)),
            requires_audible_output=True,
            repair_attempt=MAX_SAME_EDL_REPAIR_ATTEMPTS,
        )
    )

    assert verdict.disposition is ReviewDisposition.BLOCKED
    assert verdict.correction_route is ReviewCorrectionRoute.ESCALATE_OWNER
    assert verdict.report.findings[0].severity.value == "blocking"


def test_non_retryable_render_failure_routes_to_authoritative_owner() -> None:
    edl_ref = EntityRevisionRef("edl-invalid", 1)
    diagnostic = RenderDiagnostic(RenderDiagnosticCode.INVALID_EDL, "canonical EDL invalid")
    qc = FakeRenderedMediaQc(_qc(Path("unused.mp4")))

    verdict = _runtime(qc).review(
        ReviewRequest(edl_ref, RenderResult(None, (diagnostic,)), requires_audible_output=True)
    )

    assert verdict.disposition is ReviewDisposition.BLOCKED
    assert verdict.report.findings[0].affected_owner == "EDLBuilder"
    assert qc.calls == []


def test_review_runtime_exposes_no_edit_or_render_mutation_api(tmp_path: Path) -> None:
    qc = FakeRenderedMediaQc(_qc(tmp_path / "unused.mp4"))
    runtime = _runtime(qc)

    assert hasattr(runtime, "review")
    assert not hasattr(runtime, "render")
    assert not hasattr(runtime, "edit")
    assert not hasattr(runtime, "build_edl")
