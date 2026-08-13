from __future__ import annotations

import hashlib
import math
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
        if width != 2:
            raise ValueError("wave-energy baseline supports 16-bit PCM WAV only")
        energies = [
            _pcm16_rms(raw[offset : offset + stride])
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
        intervals_index = [
            right - left for left, right in zip(separated, separated[1:], strict=False)
        ]
        median_interval = (
            sorted(intervals_index)[len(intervals_index) // 2] if intervals_index else 0
        )
        periodicity = (
            0.0
            if not intervals_index or median_interval == 0
            else max(
                0.0,
                1.0
                - sum(abs(item - median_interval) for item in intervals_index)
                / (len(intervals_index) * median_interval),
            )
        )
        contrast = 0.0 if maximum == 0 else (maximum - min(energies, default=0)) / maximum
        confidence = min(1.0, periodicity * contrast)
        beats = tuple(
            BeatPoint(
                source_range.start + MediaTime(index * hop, rate),
                energies[index] / maximum,
                confidence,
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
            "r0.10b-v1",
            confidence,
            tuple(
                BeatPoint(
                    source_range.start + MediaTime(index * hop, rate),
                    energy / maximum,
                    confidence,
                )
                for index, energy in enumerate(energies)
            ),
        )


def _pcm16_rms(raw: bytes) -> int:
    if len(raw) % 2:
        raise ValueError("PCM16 payload must contain complete samples")
    samples = (
        int.from_bytes(raw[index : index + 2], "little", signed=True)
        for index in range(0, len(raw), 2)
    )
    total = sum(sample * sample for sample in samples)
    count = len(raw) // 2
    return 0 if count == 0 else math.isqrt(total // count)
