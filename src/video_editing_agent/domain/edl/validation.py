from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from video_editing_agent.domain.edl.model import EDL, EDLSegment


class EDLDiagnosticCode(StrEnum):
    DUPLICATE_SEGMENT_ID = "duplicate_segment_id"
    DUPLICATE_TRACK_ID = "duplicate_track_id"
    UNKNOWN_TRACK = "unknown_track"
    DURATION_MISMATCH = "duration_mismatch"
    SAME_TRACK_OVERLAP = "same_track_overlap"


@dataclass(frozen=True, slots=True)
class EDLDiagnostic:
    code: EDLDiagnosticCode
    message: str
    segment_ids: tuple[str, ...] = ()
    track_id: str | None = None


@dataclass(frozen=True, slots=True)
class EDLValidationResult:
    diagnostics: tuple[EDLDiagnostic, ...]

    @property
    def is_valid(self) -> bool:
        return not self.diagnostics


def _overlap_findings(segments: tuple[EDLSegment, ...]) -> list[EDLDiagnostic]:
    findings: list[EDLDiagnostic] = []
    by_track: dict[str, list[EDLSegment]] = {}
    for segment in segments:
        by_track.setdefault(segment.track_id, []).append(segment)
    for track_id in sorted(by_track):
        ordered = sorted(
            by_track[track_id],
            key=lambda item: (
                item.timeline_range.start.as_fraction(),
                item.timeline_range.end.as_fraction(),
                item.segment_id,
            ),
        )
        for previous, current in zip(ordered, ordered[1:], strict=False):
            if (
                current.timeline_range.start.as_fraction()
                < previous.timeline_range.end.as_fraction()
            ):
                findings.append(
                    EDLDiagnostic(
                        code=EDLDiagnosticCode.SAME_TRACK_OVERLAP,
                        message="segments on the same track must not overlap",
                        segment_ids=(previous.segment_id, current.segment_id),
                        track_id=track_id,
                    )
                )
    return findings


def validate_edl(edl: EDL) -> EDLValidationResult:
    """Validate locally provable timeline invariants without repairing the EDL."""

    diagnostics: list[EDLDiagnostic] = []
    seen_segments: set[str] = set()
    for segment in edl.segments:
        if segment.segment_id in seen_segments:
            diagnostics.append(
                EDLDiagnostic(
                    code=EDLDiagnosticCode.DUPLICATE_SEGMENT_ID,
                    message="segment_id values must be unique",
                    segment_ids=(segment.segment_id,),
                )
            )
        seen_segments.add(segment.segment_id)

    seen_tracks: set[str] = set()
    for track in edl.effective_tracks:
        if track.track_id in seen_tracks:
            diagnostics.append(
                EDLDiagnostic(
                    code=EDLDiagnosticCode.DUPLICATE_TRACK_ID,
                    message="track_id values must be unique",
                    track_id=track.track_id,
                )
            )
        seen_tracks.add(track.track_id)

    known_tracks = {track.track_id for track in edl.effective_tracks}
    for segment in edl.segments:
        if segment.track_id not in known_tracks:
            diagnostics.append(
                EDLDiagnostic(
                    code=EDLDiagnosticCode.UNKNOWN_TRACK,
                    message="segment references an undefined or unsupported track",
                    segment_ids=(segment.segment_id,),
                    track_id=segment.track_id,
                )
            )
        if segment.source_range.duration != segment.timeline_range.duration:
            diagnostics.append(
                EDLDiagnostic(
                    code=EDLDiagnosticCode.DURATION_MISMATCH,
                    message="source and timeline duration must match until rate mapping is typed",
                    segment_ids=(segment.segment_id,),
                    track_id=segment.track_id,
                )
            )

    diagnostics.extend(_overlap_findings(edl.segments))
    diagnostics.sort(key=lambda item: (item.code.value, item.track_id or "", item.segment_ids))
    return EDLValidationResult(diagnostics=tuple(diagnostics))
