import struct
import wave

from video_editing_agent.music.audio_editorial import inspect_pcm16_wav


def test_rendered_qc_detects_clipped_control(tmp_path) -> None:
    path = tmp_path / "clipped.wav"
    with wave.open(str(path), "wb") as stream:
        stream.setparams((1, 2, 8000, 4, "NONE", "PCM16"))
        stream.writeframes(b"".join(struct.pack("<h", value) for value in (0, 32767, -32768, 100)))
    result = inspect_pcm16_wav(str(path))
    assert result.clipped_samples == 2
    assert "clipped PCM samples detected" in result.warnings
