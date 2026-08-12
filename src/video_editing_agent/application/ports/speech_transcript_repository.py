from __future__ import annotations

from typing import Protocol

from video_editing_agent.domain.common.entity import EntityRevisionRef
from video_editing_agent.domain.evidence.speech import SpeechTranscript


class SpeechTranscriptRepository(Protocol):
    """Persist revisioned speech evidence for one exact Shot revision."""

    def save(self, transcript: SpeechTranscript) -> None: ...

    def load(self, shot_ref: EntityRevisionRef, revision: int) -> SpeechTranscript: ...

    def latest(self, shot_ref: EntityRevisionRef) -> SpeechTranscript | None: ...
