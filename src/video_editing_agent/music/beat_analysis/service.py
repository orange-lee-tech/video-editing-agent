from __future__ import annotations

import audioop
import hashlib
import wave
from datetime import UTC, datetime

from video_editing_agent.domain.common.entity import EntityEnvelope, EntityRevisionRef, EntityStatus
from video_editing_agent.domain.common.media_time import MediaTime, MediaTimeRange
from video_editing_agent.domain.music.model import BeatMap, BeatPoint


class WaveEnergyBeatAnalysisService:
    """Deterministic PCM-WAV energy peak baseline; no downbeat/section claims."""

    def analyze(
        self, path: str, asset_ref: EntityRevisionRef, source_range: MediaTimeRange
    ) -> BeatMap:
        with wave.open(path, "rb") as stream:
            rate, width, channels = (
                stream.getframerate(),
                stream.getsampwidth(),
                stream.getnchannels(),
            )
            start_frame = int(source_range.start.as_fraction() * rate)
            frame_count = int(source_range.duration.as_fraction() * rate)
            stream.setpos(start_frame)
            raw = stream.readframes(frame_count)
        hop = max(1, rate // 20)
        stride = hop * width * channels
        energies = [
            audioop.rms(raw[offset : offset + stride], width)
            for offset in range(0, len(raw), stride)
            if len(raw[offset : offset + stride]) == stride
        ]
        maximum = max(energies, default=1)
        peaks = [
            index
            for index in range(1, len(energies) - 1)
            if energies[index] > energies[index - 1]
            and energies[index] >= energies[index + 1]
            and energies[index] >= maximum * 0.45
        ]
        separated: list[int] = []
        for index in peaks:
            if not separated or index - separated[-1] >= 5:
                separated.append(index)
        beats = tuple(
            BeatPoint(
                source_range.start + MediaTime(index * hop, rate), energies[index] / maximum, 0.8
            )
            for index in separated
        )
        intervals = [
            float((right.source_time - left.source_time).as_fraction())
            for left, right in zip(beats, beats[1:], strict=False)
        ]
        tempo = None if not intervals else 60.0 / sorted(intervals)[len(intervals) // 2]
        identity = hashlib.sha256(f"{asset_ref}:{source_range}:{beats}".encode()).hexdigest()
        return BeatMap(
            EntityEnvelope(
                f"btm_{identity}",
                1,
                "0.2",
                EntityStatus.VALID,
                datetime(2026, 8, 13, tzinfo=UTC),
                "wave-energy-v1",
            ),
            asset_ref,
            source_range,
            beats,
            tempo,
            "local:wave-energy",
            "r0.10a-v1",
        )
