from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from video_editing_agent.application.ports.rendered_media_qc import (
    RenderedMediaQc,
    RenderedMediaQcCode,
    RenderedMediaQcFinding,
)
from video_editing_agent.application.ports.renderer import (
    RenderDiagnostic,
    RenderDiagnosticCode,
    RenderResult,
)
from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.review.model import (
    FindingSeverity,
    ReviewCorrectionRoute,
    ReviewDisposition,
    ReviewFinding,
    ReviewReport,
    ReviewStage,
    ReviewVerdict,
)

MAX_SAME_EDL_REPAIR_ATTEMPTS = 1


@dataclass(frozen=True, slots=True)
class ReviewRequest:
    edl_ref: EntityRevisionRef
    render_result: RenderResult
    requires_audible_output: bool
    repair_attempt: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.requires_audible_output, bool):
            raise TypeError("requires_audible_output must be a bool")
        if (
            isinstance(self.repair_attempt, bool)
            or not isinstance(self.repair_attempt, int)
            or self.repair_attempt < 0
        ):
            raise ValueError("repair_attempt must be a non-negative int")


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _diagnostic_owner(code: RenderDiagnosticCode) -> str:
    if code in {
        RenderDiagnosticCode.INVALID_EDL,
        RenderDiagnosticCode.UNSUPPORTED_TRACK,
        RenderDiagnosticCode.UNSUPPORTED_AUTOMATION,
        RenderDiagnosticCode.TIMELINE_NOT_CONTIGUOUS,
        RenderDiagnosticCode.SUBTITLE_TIMING_UNREPRESENTABLE,
        RenderDiagnosticCode.SUBTITLE_LAYER_UNSUPPORTED,
    }:
        return "EDLBuilder"
    if code in {
        RenderDiagnosticCode.MISSING_ASSET_MEDIA,
        RenderDiagnosticCode.AMBIGUOUS_ASSET_MEDIA,
        RenderDiagnosticCode.OUTPUT_CONFLICT,
    }:
        return "Application/AssetMedia"
    return "Renderer/Environment"


class ReviewApplicationRuntime:
    """Classify delivered-output evidence and route correction without editing or rendering."""

    def __init__(
        self,
        rendered_media_qc: RenderedMediaQc,
        *,
        clock: Callable[[], datetime] = _utcnow,
    ) -> None:
        self._rendered_media_qc = rendered_media_qc
        self._clock = clock

    def review(self, request: ReviewRequest) -> ReviewVerdict:
        render_result = request.render_result
        if render_result.artifact is None:
            return self._review_render_failure(request, render_result.diagnostics)
        if render_result.diagnostics:
            finding = self._finding(
                request,
                "render-result-contradiction",
                FindingSeverity.BLOCKING,
                "RenderResult contains both an artifact and diagnostics",
                "escalate contradictory render evidence",
                "Renderer/Application",
                ("render_result:artifact_and_diagnostics",),
            )
            return self._verdict(
                request,
                ReviewDisposition.BLOCKED,
                ReviewCorrectionRoute.ESCALATE_OWNER,
                (finding,),
            )

        artifact = render_result.artifact
        if artifact.edl_ref != request.edl_ref:
            finding = self._finding(
                request,
                "artifact-edl-provenance-mismatch",
                FindingSeverity.BLOCKING,
                "RenderArtifact does not match the exact canonical EDL revision under review",
                "resolve exact EDL/artifact provenance before review",
                "Application",
                (
                    f"requested_edl:{request.edl_ref.entity_id}@{request.edl_ref.revision}",
                    f"artifact_edl:{artifact.edl_ref.entity_id}@{artifact.edl_ref.revision}",
                ),
            )
            return self._verdict(
                request,
                ReviewDisposition.BLOCKED,
                ReviewCorrectionRoute.ESCALATE_OWNER,
                (finding,),
            )

        qc = self._rendered_media_qc.inspect(artifact.path)
        blocked_qc = tuple(
            item
            for item in qc.findings
            if item.code
            in {
                RenderedMediaQcCode.OUTPUT_MISSING,
                RenderedMediaQcCode.INSPECTION_FAILED,
            }
        )
        if blocked_qc:
            findings = tuple(self._blocked_qc_finding(request, item) for item in blocked_qc)
            return self._verdict(
                request,
                ReviewDisposition.BLOCKED,
                ReviewCorrectionRoute.ESCALATE_OWNER,
                findings,
            )

        if qc.has_code(RenderedMediaQcCode.NO_AUDIO_STREAM):
            if not request.requires_audible_output:
                return self._verdict(
                    request,
                    ReviewDisposition.PASS,
                    ReviewCorrectionRoute.NONE,
                    (),
                )
            finding = self._finding(
                request,
                "audible-intent-without-delivered-audio-stream",
                FindingSeverity.BLOCKING,
                "audible output is required but delivered media exposes no audio stream",
                "reconcile audible intent with the canonical EDL before a new render",
                "AudioEditorialService/Application",
                (f"artifact:{artifact.path}", "qc:no_audio_stream"),
            )
            return self._verdict(
                request,
                ReviewDisposition.BLOCKED,
                ReviewCorrectionRoute.ESCALATE_OWNER,
                (finding,),
            )

        correction_findings: list[ReviewFinding] = []
        if qc.has_code(RenderedMediaQcCode.CLIPPING):
            correction_findings.append(
                self._finding(
                    request,
                    "delivered-audio-clipping",
                    FindingSeverity.MAJOR,
                    "post-render PCM evidence contains clipped samples",
                    "return evidence to AudioEditorialService for a fresh approved mix decision",
                    "AudioEditorialService",
                    (
                        f"artifact:{artifact.path}",
                        f"qc:clipped_samples={qc.clipped_samples}",
                    ),
                )
            )
        if request.requires_audible_output and qc.has_code(RenderedMediaQcCode.MOSTLY_SILENT):
            correction_findings.append(
                self._finding(
                    request,
                    "delivered-audio-unexpectedly-silent",
                    FindingSeverity.MAJOR,
                    "post-render PCM evidence is mostly silent despite audible output intent",
                    "return evidence to AudioEditorialService for a fresh approved mix decision",
                    "AudioEditorialService",
                    (
                        f"artifact:{artifact.path}",
                        f"qc:silent_fraction={qc.silent_fraction}",
                    ),
                )
            )
        if correction_findings:
            return self._verdict(
                request,
                ReviewDisposition.CORRECTION_REQUIRED,
                ReviewCorrectionRoute.RETURN_TO_AUDIO_EDITORIAL,
                tuple(correction_findings),
            )

        return self._verdict(
            request,
            ReviewDisposition.PASS,
            ReviewCorrectionRoute.NONE,
            (),
        )

    def _review_render_failure(
        self, request: ReviewRequest, diagnostics: tuple[RenderDiagnostic, ...]
    ) -> ReviewVerdict:
        if not diagnostics:
            finding = self._finding(
                request,
                "render-result-missing-evidence",
                FindingSeverity.BLOCKING,
                "RenderResult has neither an artifact nor diagnostics",
                "obtain typed render evidence before review",
                "Renderer/Application",
                ("render_result:no_artifact_no_diagnostics",),
            )
            return self._verdict(
                request,
                ReviewDisposition.BLOCKED,
                ReviewCorrectionRoute.ESCALATE_OWNER,
                (finding,),
            )

        retryable_codes = {
            RenderDiagnosticCode.EXECUTION_FAILED,
            RenderDiagnosticCode.OUTPUT_VERIFICATION_FAILED,
        }
        if all(item.code in retryable_codes for item in diagnostics):
            if request.repair_attempt < MAX_SAME_EDL_REPAIR_ATTEMPTS:
                findings = tuple(
                    self._render_diagnostic_finding(
                        request,
                        item,
                        severity=FindingSeverity.MAJOR,
                        action="rerender the same exact EDL without changing editorial decisions",
                    )
                    for item in diagnostics
                )
                return self._verdict(
                    request,
                    ReviewDisposition.CORRECTION_REQUIRED,
                    ReviewCorrectionRoute.RERENDER_SAME_EDL,
                    findings,
                )
            findings = tuple(
                self._render_diagnostic_finding(
                    request,
                    item,
                    severity=FindingSeverity.BLOCKING,
                    action="same-EDL retry bound exhausted; escalate renderer/environment evidence",
                )
                for item in diagnostics
            )
            return self._verdict(
                request,
                ReviewDisposition.BLOCKED,
                ReviewCorrectionRoute.ESCALATE_OWNER,
                findings,
            )

        findings = tuple(
            self._render_diagnostic_finding(
                request,
                item,
                severity=FindingSeverity.BLOCKING,
                action="return to the named authoritative owner before rendering again",
            )
            for item in diagnostics
        )
        return self._verdict(
            request,
            ReviewDisposition.BLOCKED,
            ReviewCorrectionRoute.ESCALATE_OWNER,
            findings,
        )

    def _render_diagnostic_finding(
        self,
        request: ReviewRequest,
        diagnostic: RenderDiagnostic,
        *,
        severity: FindingSeverity,
        action: str,
    ) -> ReviewFinding:
        return self._finding(
            request,
            f"render-{diagnostic.code.value}",
            severity,
            diagnostic.message,
            action,
            _diagnostic_owner(diagnostic.code),
            (f"render_diagnostic:{diagnostic.code.value}",),
        )

    def _blocked_qc_finding(
        self, request: ReviewRequest, finding: RenderedMediaQcFinding
    ) -> ReviewFinding:
        return self._finding(
            request,
            f"media-qc-{finding.code.value}",
            FindingSeverity.BLOCKING,
            finding.message,
            "restore inspectable delivered-media evidence before acceptance",
            "RenderedMediaQc/Environment",
            (f"media_qc:{finding.code.value}",),
        )

    def _finding(
        self,
        request: ReviewRequest,
        suffix: str,
        severity: FindingSeverity,
        problem: str,
        recommended_action: str,
        affected_owner: str,
        evidence_refs: tuple[str, ...],
    ) -> ReviewFinding:
        return ReviewFinding(
            f"review:{request.edl_ref.entity_id}:r{request.edl_ref.revision}:{suffix}",
            severity,
            problem,
            recommended_action,
            affected_owner,
            evidence_refs=evidence_refs,
        )

    def _verdict(
        self,
        request: ReviewRequest,
        disposition: ReviewDisposition,
        route: ReviewCorrectionRoute,
        findings: tuple[ReviewFinding, ...],
    ) -> ReviewVerdict:
        passed = disposition is ReviewDisposition.PASS
        report = ReviewReport(
            EntityEnvelope(
                id=(
                    f"review:{request.edl_ref.entity_id}:r{request.edl_ref.revision}:"
                    f"attempt{request.repair_attempt}"
                ),
                revision=1,
                schema_version="review-report/v1",
                status=EntityStatus.VALID,
                created_at=self._clock(),
                created_by="ReviewApplicationRuntime",
                derived_from=(request.edl_ref,),
            ),
            ReviewStage.FINAL_TECHNICAL_QC,
            request.edl_ref,
            passed,
            findings,
        )
        return ReviewVerdict(disposition, report, route, request.repair_attempt)
