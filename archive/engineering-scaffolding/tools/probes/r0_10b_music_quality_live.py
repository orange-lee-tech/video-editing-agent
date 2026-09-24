from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import struct
import subprocess
import sys
import time
import wave
from dataclasses import replace
from datetime import UTC, datetime

from video_editing_agent.application.ports.audio_editorial import AudioTrackRole, SourceAudioPolicy
from video_editing_agent.application.ports.music_selection import MusicIntent
from video_editing_agent.domain.asset.rights import RightsAttestation
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


def fixture(path: pathlib.Path, *, weak: bool = False) -> None:
    rate, duration = 48_000, 12
    with wave.open(str(path), "wb") as stream:
        stream.setparams((1, 2, rate, duration * rate, "NONE", "PCM16"))
        frames = bytearray()
        for index in range(duration * rate):
            t = index / rate
            pulse = 0.1 if weak else math.exp(-18 * (t % 0.5)) * (0.45 + 0.55 * t / duration)
            frames.extend(struct.pack("<h", int(11_000 * math.sin(2 * math.pi * 220 * t) * pulse)))
        stream.writeframes(frames)


def render(
    ffmpeg: str, video: pathlib.Path, music: pathlib.Path, output: pathlib.Path, *, structured: bool
) -> None:
    bgm = "volume=0.3,afade=t=in:st=0:d=0.5,afade=t=out:st=5.5:d=0.5"
    if structured:
        bgm += ",volume='if(between(t,0.75,3.5)+between(t,3.75,5.5),0.28,1)':eval=frame"
    subprocess.run(
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
            f"[0:a]atrim=0:6,asetpts=PTS-STARTPTS[src];[1:a]atrim=0:6,asetpts=PTS-STARTPTS,{bgm}[bgm];[src][bgm]amix=inputs=2:duration=first:normalize=0[a]",
            "-map",
            "0:v",
            "-map",
            "[a]",
            "-t",
            "6",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            str(output),
        ],
        check=True,
    )


def render_structured(ffmpeg, video, music, output, selection, mix):
    plan = compile_audio_execution(selection, mix)
    subprocess.run(
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
            plan.filter_complex,
            "-map",
            "0:v",
            "-map",
            "[a]",
            "-t",
            plan.output_duration_seconds,
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            str(output),
        ],
        check=True,
    )
    return plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--ffmpeg", required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    args.output.mkdir(parents=True, exist_ok=True)
    music, weak = args.output / "structured_music.wav", args.output / "weak_music.wav"
    fixture(music)
    fixture(weak, weak=True)
    ref = EntityRevisionRef("ast_r0_10b_music", 1)
    attestation = RightsAttestation(
        "att_r0_10b",
        ref,
        "engineering-probe",
        datetime(2026, 8, 13, tzinfo=UTC),
        "local-only generated fixture",
    )
    analysis_started = time.perf_counter()
    service = WaveEnergyBeatAnalysisService()
    beatmap = service.analyze(str(music), ref, MediaTimeRange(MediaTime(0, 1), MediaTime(12, 1)))
    weak_map = service.analyze(str(weak), ref, MediaTimeRange(MediaTime(0, 1), MediaTime(12, 1)))
    analysis_seconds = time.perf_counter() - analysis_started
    speech = (
        MediaTimeRange(MediaTime(1, 1), MediaTime(2, 1)),
        MediaTimeRange(MediaTime(4, 1), MediaTime(1, 1)),
    )
    windows = generate_music_windows(
        beatmap,
        MediaTime(3, 1),
        (attestation.attestation_id,),
        MusicIntent("rising energy", MediaTime(6, 1), mood_tags=("high",)),
        WindowScoringPolicy(speech_ranges=speech),
    )
    selection = select_music(windows, target_duration=MediaTime(6, 1))
    assert selection is not None
    mix = plan_basic_mix(EntityRevisionRef("plan_r0_10b", 1), ref, MediaTime(6, 1), speech)
    render_started = time.perf_counter()
    baseline = args.output / "baseline_mix_preview.mp4"
    structured = args.output / "structured_mix_preview.mp4"
    muted_source = args.output / "muted_source_mix_preview.mp4"
    render(args.ffmpeg, args.video, music, baseline, structured=False)
    execution = render_structured(args.ffmpeg, args.video, music, structured, selection, mix)
    muted_execution = render_structured(
        args.ffmpeg,
        args.video,
        music,
        muted_source,
        selection,
        replace(mix, source_audio_policy=SourceAudioPolicy.MUTE),
    )
    rendered_pcm = args.output / "structured_mix_qc.wav"
    subprocess.run(
        [
            args.ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(structured),
            "-vn",
            "-c:a",
            "pcm_s16le",
            str(rendered_pcm),
        ],
        check=True,
    )
    qc = inspect_pcm16_wav(str(rendered_pcm))
    muted_pcm = args.output / "muted_source_mix_qc.wav"
    subprocess.run(
        [
            args.ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(muted_source),
            "-vn",
            "-c:a",
            "pcm_s16le",
            str(muted_pcm),
        ],
        check=True,
    )
    muted_qc = inspect_pcm16_wav(str(muted_pcm))
    render_seconds = time.perf_counter() - render_started
    gates = {
        "PYTHON_SUPPORT_COMPATIBLE": "audioop"
        not in pathlib.Path(__file__)
        .parents[2]
        .joinpath("src/video_editing_agent/music/beat_analysis/service.py")
        .read_text(),
        "AUTOMATION_TARGET_SEMANTICS": all(
            item.target_role is AudioTrackRole.BGM and not item.target_slot_ids
            for item in mix.automation_intents
        ),
        "BEATMAP_REAL_CONFIDENCE": 0 < beatmap.confidence <= 1
        and len({item.energy for item in beatmap.energy_envelope}) > 1,
        "WEAK_RHYTHM_FAILS_SOFT": weak_map.confidence < beatmap.confidence
        and weak_map.tempo_bpm is None,
        "WINDOW_FEATURES_INSPECTABLE": all(
            item.feature_contributions and item.reasons for item in windows
        )
        and len({item.score for item in windows}) > 1,
        "WINDOW_RANKING_DETERMINISTIC": windows
        == generate_music_windows(
            beatmap,
            MediaTime(3, 1),
            (attestation.attestation_id,),
            MusicIntent("rising energy", MediaTime(6, 1), mood_tags=("high",)),
            WindowScoringPolicy(speech_ranges=speech),
        ),
        "RIGHTS_HARD_GATE_PRESERVED": local_rights_eligibility(ref, None).value == "unknown"
        and generate_music_windows(beatmap, MediaTime(3, 1), ()) == (),
        "STRUCTURAL_LOOP_BOUNDED_OR_REFUSED": len(selection.source_segments) == 2
        and all(item.source_range.end.as_fraction() <= 12 for item in selection.source_segments),
        "DUCK_RAMPS_BOUNDED": all(
            item.start is None or (item.start.as_fraction() >= 0 and item.end.as_fraction() <= 6)
            for item in mix.automation_intents
        ),
        "AUDIO_QC_INSPECTABLE": qc.peak_dbfs is not None
        and qc.rms_dbfs is not None
        and qc.clipped_samples == 0,
        "AUDIBLE_A_B_RENDERED": all(
            path.exists() and path.stat().st_size > 10_000 for path in (baseline, structured)
        ),
        "R0_10A_REGRESSION": len(beatmap.beats) >= 20
        and selection.rights_evidence_refs == (attestation.attestation_id,),
        "SELECTED_SEGMENTS_EXECUTED": execution.source_segments
        == tuple(item.source_range for item in selection.source_segments),
        "DECISION_AUTOMATION_COMPILED": all(
            token in execution.filter_complex
            for token in (
                "atrim=start=9.000",
                "afade=t=in",
                "between(t,0.750",
                "volume=0.316227766",
            )
        ),
        "POST_MIX_QC": rendered_pcm.exists() and qc.clipped_samples == 0,
        "SOURCE_POLICY_EXECUTION_DIFFERS": execution.consumes_source_audio
        and not muted_execution.consumes_source_audio
        and "[0:a]" in execution.filter_complex
        and "[0:a]" not in muted_execution.filter_complex,
        "SOURCE_POLICY_RENDER_DIFFERS": hashlib.sha256(structured.read_bytes()).digest()
        != hashlib.sha256(muted_source.read_bytes()).digest(),
        "MUTED_SOURCE_RETAINS_AUDIBLE_BGM": muted_qc.rms_dbfs is not None
        and muted_qc.silent_fraction < 0.95
        and muted_qc.clipped_samples == 0,
    }
    report = {
        "gates": {key: "PASS" if value else "FAIL" for key, value in gates.items()},
        "beatmap": {
            "beats": len(beatmap.beats),
            "tempo_bpm": beatmap.tempo_bpm,
            "confidence": beatmap.confidence,
            "weak_confidence": weak_map.confidence,
        },
        "windows": [
            {
                "id": item.candidate_id,
                "range": [
                    float(item.source_range.start.as_fraction()),
                    float(item.source_range.end.as_fraction()),
                ],
                "score": item.score,
                "confidence": item.confidence,
                "features": item.feature_contributions,
            }
            for item in windows
        ],
        "selection": {
            "segments": [
                [
                    float(item.source_range.start.as_fraction()),
                    float(item.source_range.end.as_fraction()),
                ]
                for item in selection.source_segments
            ],
            "score": selection.score,
            "reasons": selection.reasons,
            "warnings": selection.warnings,
        },
        "mix": {
            "automation": [
                {
                    "kind": item.kind.value,
                    "target_role": item.target_role.value if item.target_role else None,
                    "range": None
                    if item.start is None
                    else [float(item.start.as_fraction()), float(item.end.as_fraction())],
                }
                for item in mix.automation_intents
            ]
        },
        "execution": {
            "selected_asset_id": execution.selected_asset_id,
            "source_audio_policy": execution.source_audio_policy.value,
            "consumes_source_audio": execution.consumes_source_audio,
            "source_segments": [
                [float(item.start.as_fraction()), float(item.end.as_fraction())]
                for item in execution.source_segments
            ],
            "filter_complex": execution.filter_complex,
        },
        "muted_execution": {
            "source_audio_policy": muted_execution.source_audio_policy.value,
            "consumes_source_audio": muted_execution.consumes_source_audio,
            "filter_complex": muted_execution.filter_complex,
        },
        "qc": {
            "peak_dbfs": qc.peak_dbfs,
            "rms_dbfs": qc.rms_dbfs,
            "silent_fraction": qc.silent_fraction,
            "clipped_samples": qc.clipped_samples,
            "warnings": qc.warnings,
        },
        "muted_qc": {
            "peak_dbfs": muted_qc.peak_dbfs,
            "rms_dbfs": muted_qc.rms_dbfs,
            "silent_fraction": muted_qc.silent_fraction,
            "clipped_samples": muted_qc.clipped_samples,
            "warnings": muted_qc.warnings,
        },
        "timings_seconds": {
            "analysis": analysis_seconds,
            "render": render_seconds,
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
