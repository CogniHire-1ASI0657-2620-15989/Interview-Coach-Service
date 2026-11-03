from dataclasses import dataclass, field
from datetime import datetime

from app.domain.model.entities.interview_report import InterviewReport
from app.domain.model.entities.transcript_message import TranscriptMessage
from app.domain.model.value_objects.interview_mode import InterviewMode
from app.domain.model.value_objects.interview_session_status import InterviewSessionStatus
from app.domain.model.value_objects.message_speaker import MessageSpeaker


@dataclass
class InterviewSession:
    MAX_QUESTIONS = 6

    id: int | None
    user_id: int
    job_id: int
    job_title: str
    job_description: str | None
    user_segment: str
    mode: InterviewMode
    status: InterviewSessionStatus
    question_count: int
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    messages: list[TranscriptMessage] = field(default_factory=list)
    report: InterviewReport | None = None

    def __post_init__(self) -> None:
        if self.user_id <= 0 or self.job_id <= 0:
            raise ValueError("user_id and job_id must be positive.")
        if not self.job_title.strip():
            raise ValueError("job_title cannot be blank.")
        if not self.user_segment.strip():
            raise ValueError("user_segment cannot be blank.")
        if not 0 <= self.question_count <= self.MAX_QUESTIONS:
            raise ValueError(f"question_count must be between 0 and {self.MAX_QUESTIONS}.")

    @property
    def can_ask_another_question(self) -> bool:
        return self.status == InterviewSessionStatus.ACTIVE and self.question_count < self.MAX_QUESTIONS

    def add_message(self, speaker: MessageSpeaker, content: str, created_at: datetime) -> TranscriptMessage:
        normalized_content = content.strip()
        if not normalized_content:
            raise ValueError("Interview messages cannot be blank.")
        if self.status != InterviewSessionStatus.ACTIVE:
            raise ValueError("Messages can only be added to an active interview session.")
        if speaker == MessageSpeaker.COACH and not self.can_ask_another_question:
            raise ValueError(f"An interview session cannot exceed {self.MAX_QUESTIONS} questions.")

        message = TranscriptMessage(
            id=None,
            session_id=self.id,
            sequence=len(self.messages) + 1,
            speaker=speaker,
            content=normalized_content,
            created_at=created_at,
        )
        self.messages.append(message)
        if speaker == MessageSpeaker.COACH:
            self.question_count += 1
        self.updated_at = created_at
        return message

    def complete(self, report: InterviewReport, completed_at: datetime) -> None:
        if self.status != InterviewSessionStatus.ACTIVE:
            raise ValueError("Only an active interview session can be completed.")
        self.status = InterviewSessionStatus.COMPLETED
        self.report = report
        self.completed_at = completed_at
        self.updated_at = completed_at

    def abandon(self, abandoned_at: datetime) -> None:
        if self.status != InterviewSessionStatus.ACTIVE:
            raise ValueError("Only an active interview session can be abandoned.")
        self.status = InterviewSessionStatus.ABANDONED
        self.updated_at = abandoned_at
