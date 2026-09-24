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
from datetime import UTC, datetime

from video_editing_agent.domain.asset.rights import RightsAttestation, RightsEligibility
from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.music.audio_editorial import plan_basic_mix
from video_editing_agent.music.beat_analysis.service import WaveEnergyBeatAnalysisService
from video_editing_agent.music.selection.service import (
    generate_music_windows,
    local_rights_eligibility,
    select_music,
)


def _fixture(path: pathlib.Path) -> None:
    rate, duration = 48_000, 12
    with wave.open(str(path), "wb") as stream:
        stream.setparams((1, 2, rate, duration * rate, "NONE", "not compressed"))
        frames = bytearray()
        for index in range(duration * rate):
            phase = index / rate
            pulse = math.exp(-18 * (phase % 0.5))
            value = int(12_000 * math.sin(2 * math.pi * 220 * phase) * (0.25 + 0.75 * pulse))
            frames.extend(struct.pack("<h", value))
        stream.writeframes(frames)


def _time(value: MediaTime) -> float:
    return float(value.as_fraction())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--ffmpeg", required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    args.output.mkdir(parents=True, exist_ok=True)
    music_path = args.output / "deterministic_local_only_music.wav"
    _fixture(music_path)
    ref = EntityRevisionRef("ast_probe_music", 1)
    unknown = local_rights_eligibility(ref, None)
    attestation = RightsAttestation(
        "att_probe_music",
        ref,
        "engineering-probe",
        datetime(2026, 8, 13, tzinfo=UTC),
        "Deterministic local-only fixture generated for this engineering probe",
    )
    rights = local_rights_eligibility(ref, attestation)
    beat_started = time.perf_counter()
    beatmap = WaveEnergyBeatAnalysisService().analyze(
        str(music_path), ref, MediaTimeRange(MediaTime(0, 1), MediaTime(12, 1))
    )
    beat_seconds = time.perf_counter() - beat_started
    repeat = WaveEnergyBeatAnalysisService().analyze(
        str(music_path), ref, beatmap.analyzed_source_range
    )
    windows = generate_music_windows(beatmap, MediaTime(6, 1), (attestation.attestation_id,))
    selection = select_music(windows)
    if selection is None:
        raise RuntimeError("rights-eligible BeatMap produced no grounded music window")
    speech = (
        MediaTimeRange(MediaTime(1, 1), MediaTime(2, 1)),
        MediaTimeRange(MediaTime(4, 1), MediaTime(1, 1)),
    )
    mix = plan_basic_mix(EntityRevisionRef("plan_probe", 1), ref, MediaTime(6, 1), speech)
    selected = selection.source_segments[0].source_range
    preview = args.output / "audible_mix_preview.mp4"
    render_started = time.perf_counter()
    enable = "+".join(f"between(t,{_time(item.start)},{_time(item.end)})" for item in speech)
    subprocess.run(
        [
            args.ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(args.video),
            "-ss",
            selected.start.to_decimal_seconds_string(),
            "-t",
            selected.duration.to_decimal_seconds_string(),
            "-i",
            str(music_path),
            "-filter_complex",
            f"[0:a]atrim=0:6,asetpts=PTS-STARTPTS[src];[1:a]atrim=0:6,asetpts=PTS-STARTPTS,volume=0.32,volume=0.25:enable='{enable}',afade=t=in:st=0:d=0.5,afade=t=out:st=5.5:d=0.5[bgm];[src][bgm]amix=inputs=2:duration=first:normalize=0[a]",
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
            str(preview),
        ],
        check=True,
    )
    render_seconds = time.perf_counter() - render_started
    gates = {
        "LOCAL_RIGHTS_REQUIRED": unknown is RightsEligibility.UNKNOWN
        and rights is RightsEligibility.ELIGIBLE,
        "INELIGIBLE_CANNOT_WIN": generate_music_windows(beatmap, MediaTime(6, 1), ()) == (),
        "BEATMAP_SOURCE_TIME_BOUNDED": all(x.source_time.as_fraction() < 12 for x in beatmap.beats),
        "BEATMAP_DETERMINISTIC": beatmap == repeat,
        "MUSIC_WINDOW_GROUNDED": bool(windows)
        and all(x.beat_map_ref.entity_id == beatmap.envelope.id for x in windows),
        "MUSIC_WINDOW_INSIDE_ASSET": all(x.source_range.end.as_fraction() <= 12 for x in windows),
        "SELECTION_PRESERVES_RIGHTS_PROVENANCE": selection.rights_evidence_refs
        == (attestation.attestation_id,),
        "SPEECH_DUCKING_EXPLICIT": sum(x.kind.value == "duck" for x in mix.automation_intents) == 2,
        "AUDIO_MIX_NO_AUTHORITY_LEAK": selection.source_segments[0].source_range == selected,
        "AUDIBLE_PREVIEW_RENDERED": preview.exists() and preview.stat().st_size > 10_000,
    }
    beat_report = {
        "beat_count": len(beatmap.beats),
        "tempo_bpm": beatmap.tempo_bpm,
        "source_range_seconds": [0, 12],
        "beats_seconds": [_time(x.source_time) for x in beatmap.beats],
    }
    selection_report = {
        "rights_eligibility": rights.value,
        "rights_evidence_refs": selection.rights_evidence_refs,
        "candidate_window_count": len(windows),
        "selected_range_seconds": [_time(selected.start), _time(selected.end)],
        "decision_id": selection.decision_id,
    }
    mix_report = {
        "source_audio_policy": mix.source_audio_policy.value,
        "automation": [
            {
                "kind": x.kind.value,
                "gain_db": x.gain_db,
                "range_seconds": None if x.start is None else [_time(x.start), _time(x.end)],
                "evidence_refs": x.evidence_refs,
            }
            for x in mix.automation_intents
        ],
    }
    (args.output / "beatmap.json").write_text(
        json.dumps(beat_report, indent=2, sort_keys=True), encoding="utf-8"
    )
    (args.output / "music_selection.json").write_text(
        json.dumps(selection_report, indent=2, sort_keys=True), encoding="utf-8"
    )
    (args.output / "audio_mix_decision.json").write_text(
        json.dumps(mix_report, indent=2, sort_keys=True), encoding="utf-8"
    )
    result = {
        "gates": {key: "PASS" if value else "FAIL" for key, value in gates.items()},
        "beatmap": beat_report,
        "selection": selection_report,
        "mix": mix_report,
        "fixture_sha256": hashlib.sha256(music_path.read_bytes()).hexdigest(),
        "timings_seconds": {
            "beat_analysis": beat_seconds,
            "render": render_seconds,
            "total": time.perf_counter() - started,
        },
        "pass": all(gates.values()),
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
