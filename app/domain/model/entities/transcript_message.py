from dataclasses import dataclass
from datetime import datetime

from app.domain.model.value_objects.message_speaker import MessageSpeaker


@dataclass
class TranscriptMessage:
    id: int | None
    session_id: int | None
    sequence: int
    speaker: MessageSpeaker
    content: str
    created_at: datetime
