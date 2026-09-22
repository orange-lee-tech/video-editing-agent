from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import time
from dataclasses import replace
from datetime import UTC, datetime
from fractions import Fraction

from video_editing_agent.application.ports.audio_editorial import AudioAutomationKind
from video_editing_agent.application.ports.music_selection import MusicIntent
from video_editing_agent.domain.asset.rights import RightsAttestation, RightsEligibility
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.music.audio_editorial import inspect_pcm16_wav, plan_basic_mix
from video_editing_agent.music.beat_analysis.service import WaveEnergyBeatAnalysisService
from video_editing_agent.music.execution import compile_audio_execution
from video_editing_agent.music.selection.service import (
    WindowScoringPolicy,
    generate_music_windows,
    local_rights_eligibility,
    select_music,
)

TARGET = MediaTime(6, 1)
ANALYSIS_LIMIT_SECONDS = 60


def _run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _probe_duration(ffprobe: str, path: pathlib.Path) -> Fraction:
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return Fraction(result.stdout.strip())


def _decode_analysis_audio(
    ffmpeg: str, source: pathlib.Path, output: pathlib.Path, duration: MediaTime
) -> None:
    _run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-t",
            duration.to_decimal_seconds_string(),
            "-vn",
            "-ac",
            "2",
            "-ar",
            "48000",
            "-c:a",
            "pcm_s16le",
            str(output),
        ]
    )


def _render(
    ffmpeg: str, video: pathlib.Path, music: pathlib.Path, output: pathlib.Path, selection, mix
):
    execution = compile_audio_execution(selection, mix)
    _run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video),
            "-i",
            str(music),
            "-filter_complex",
            execution.filter_complex,
            "-map",
            "0:v",
            "-map",
            "[a]",
            "-t",
            execution.output_duration_seconds,
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            str(output),
        ]
    )
    return execution


def _qc(ffmpeg: str, preview: pathlib.Path, output: pathlib.Path):
    _run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(preview),
            "-vn",
            "-c:a",
            "pcm_s16le",
            str(output),
        ]
    )
    return inspect_pcm16_wav(str(output))


def _seconds(value: MediaTime) -> float:
    return float(value.as_fraction())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=pathlib.Path, required=True)
    parser.add_argument("--music-dir", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--ffmpeg", required=True)
    parser.add_argument("--ffprobe", required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    tracks = sorted(path for path in args.music_dir.iterdir() if path.is_file())
    if len(tracks) < 2:
        raise RuntimeError("R0.10 Product Probe requires at least two real local music files")
    tracks = tracks[:2]
    args.output.mkdir(parents=True, exist_ok=True)

    records = []
    analysis_started = time.perf_counter()
    for index, source in enumerate(tracks, start=1):
        digest = _sha256(source)
        ref = EntityRevisionRef(f"ast_music_{digest[:16]}", 1)
        attestation = RightsAttestation(
            f"att_music_{digest[:16]}",
            ref,
            "user",
            datetime(2026, 8, 14, tzinfo=UTC),
            "User attests local test and Product Probe rights for this project",
        )
        if local_rights_eligibility(ref, attestation) is not RightsEligibility.ELIGIBLE:
            raise RuntimeError("rights-attested local music did not pass the rights gate")
        duration_fraction = min(_probe_duration(args.ffprobe, source), ANALYSIS_LIMIT_SECONDS)
        if duration_fraction < TARGET.as_fraction():
            raise RuntimeError(f"music input is shorter than {TARGET}: {source.name}")
        duration = MediaTime(duration_fraction.numerator, duration_fraction.denominator)
        decoded = args.output / f"track_{index}_analysis.wav"
        _decode_analysis_audio(args.ffmpeg, source, decoded, duration)
        beatmap = WaveEnergyBeatAnalysisService().analyze(
            str(decoded), ref, MediaTimeRange(MediaTime(0, 1), duration)
        )
        windows = generate_music_windows(
            beatmap,
            TARGET,
            (attestation.attestation_id,),
            MusicIntent("energetic short-form product video", TARGET, mood_tags=("high",)),
            WindowScoringPolicy(),
        )
        if not windows:
            raise RuntimeError(f"no grounded CandidateMusicWindow for {source.name}")
        records.append((source, digest, ref, attestation, decoded, beatmap, windows))
    analysis_seconds = time.perf_counter() - analysis_started

    candidate_windows = tuple(record[6][0] for record in reversed(records))
    winning_selection = select_music(candidate_windows)
    if winning_selection is None:
        raise RuntimeError("candidate comparison produced no MusicSelectionDecision")
    winning = next(
        record for record in records if record[2] == winning_selection.selected_asset_ref
    )
    structured_mix = plan_basic_mix(
        EntityRevisionRef("plan_r0_10_product_probe", 1),
        winning[2],
        TARGET,
        (),
    )
    gain_only = tuple(
        intent
        for intent in structured_mix.automation_intents
        if intent.kind is AudioAutomationKind.GAIN
    )
    basic_mix = replace(
        structured_mix,
        decision_id=f"{structured_mix.decision_id}_basic",
        automation_intents=gain_only,
    )

    preview_specs = []
    for label, record in zip(("a", "b"), records, strict=True):
        selection = select_music((record[6][0],))
        assert selection is not None
        candidate_mix = plan_basic_mix(
            EntityRevisionRef("plan_r0_10_product_probe", 1), record[2], TARGET, ()
        )
        preview_specs.append((f"candidate_{label}", record, selection, candidate_mix))

    selected_windows = winning[6]
    ordinary_selection = select_music((selected_windows[-1],))
    selected_selection = select_music((selected_windows[0],))
    assert ordinary_selection is not None and selected_selection is not None
    preview_specs.extend(
        (
            ("moment_ordinary", winning, ordinary_selection, structured_mix),
            ("moment_selected", winning, selected_selection, structured_mix),
            ("mix_basic", winning, selected_selection, basic_mix),
            ("mix_structured", winning, selected_selection, structured_mix),
        )
    )

    rendered = {}
    render_started = time.perf_counter()
    for label, record, selection, mix in preview_specs:
        preview = args.output / f"{label}.mp4"
        execution = _render(args.ffmpeg, args.video, record[0], preview, selection, mix)
        qc = _qc(args.ffmpeg, preview, args.output / f"{label}_qc.wav")
        rendered[label] = {
            "preview": preview.name,
            "asset_id": execution.selected_asset_id,
            "decision_id": selection.decision_id,
            "mix_decision_id": mix.decision_id,
            "source_audio_policy": execution.source_audio_policy.value,
            "source_ranges_seconds": [
                [_seconds(item.start), _seconds(item.end)] for item in execution.source_segments
            ],
            "qc": {
                "peak_dbfs": qc.peak_dbfs,
                "rms_dbfs": qc.rms_dbfs,
                "silent_fraction": qc.silent_fraction,
                "clipped_samples": qc.clipped_samples,
                "warnings": qc.warnings,
            },
            "sha256": _sha256(preview),
        }
    render_seconds = time.perf_counter() - render_started

    track_report = [
        {
            "label": label,
            "file": record[0].name,
            "sha256": record[1],
            "size_bytes": record[0].stat().st_size,
            "asset_id": record[2].entity_id,
            "rights_status": local_rights_eligibility(record[2], record[3]).value,
            "analysis_range_seconds": [
                _seconds(record[5].analyzed_source_range.start),
                _seconds(record[5].analyzed_source_range.end),
            ],
            "beat_count": len(record[5].beats),
            "tempo_bpm": record[5].tempo_bpm,
            "confidence": record[5].confidence,
            "top_window_score": record[6][0].score,
            "top_window_seconds": [
                _seconds(record[6][0].source_range.start),
                _seconds(record[6][0].source_range.end),
            ],
        }
        for label, record in zip(("A", "B"), records, strict=True)
    ]
    qc_green = all(
        item["qc"]["rms_dbfs"] is not None
        and item["qc"]["silent_fraction"] < 0.95
        and item["qc"]["clipped_samples"] == 0
        for item in rendered.values()
    )
    gates = {
        "TWO_REAL_RIGHTS_ATTESTED_TRACKS": len(records) == 2
        and all(item["rights_status"] == "eligible" for item in track_report),
        "BEATMAP_AND_WINDOWS_GROUNDED": all(record[5].beats and record[6] for record in records),
        "CANONICAL_DECISIONS_EXECUTED": all(item["decision_id"] for item in rendered.values()),
        "MUSIC_CANDIDATE_A_B": rendered["candidate_a"]["asset_id"]
        != rendered["candidate_b"]["asset_id"],
        "CANDIDATE_WINNER_IS_GLOBAL_TOP_SCORE": winning_selection.selected_asset_ref
        == max(candidate_windows, key=lambda item: item.score).audio_asset_ref,
        "MUSIC_MOMENT_A_B": rendered["moment_ordinary"]["source_ranges_seconds"]
        != rendered["moment_selected"]["source_ranges_seconds"],
        "MIX_A_B": rendered["mix_basic"]["sha256"] != rendered["mix_structured"]["sha256"],
        "EVERY_PREVIEW_POST_MIX_QC": qc_green,
        "SOURCE_ASSETS_UNCHANGED": all(_sha256(record[0]) == record[1] for record in records),
    }
    report = {
        "classification": "READY_FOR_HUMAN_ACCEPTANCE" if all(gates.values()) else "TECHNICAL_FAIL",
        "rights_attestation": "user-attested local test and Product Probe use rights",
        "tracks": track_report,
        "winning_asset_id": winning_selection.selected_asset_ref.entity_id,
        "comparisons": rendered,
        "gates": {name: "PASS" if value else "FAIL" for name, value in gates.items()},
        "timings_seconds": {
            "analysis": analysis_seconds,
            "render_and_qc": render_seconds,
            "total": time.perf_counter() - started,
        },
        "pass": all(gates.values()),
    }
    (args.output / "comparison.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(report, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
