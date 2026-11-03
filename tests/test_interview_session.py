from datetime import datetime, timezone

import pytest

from app.domain.model.aggregates.interview_session import InterviewSession
from app.domain.model.value_objects.interview_mode import InterviewMode
from app.domain.model.value_objects.interview_session_status import InterviewSessionStatus
from app.domain.model.value_objects.message_speaker import MessageSpeaker


def build_session() -> InterviewSession:
    now = datetime.now(timezone.utc)
    return InterviewSession(
        id=None,
        user_id=1,
        job_id=10,
        job_title="Backend Developer",
        job_description="Develop Python services.",
        user_segment="intern",
        mode=InterviewMode.MIXED,
        status=InterviewSessionStatus.ACTIVE,
        question_count=0,
        created_at=now,
        updated_at=now,
    )


def test_session_accepts_at_most_six_coach_questions() -> None:
    session = build_session()
    now = datetime.now(timezone.utc)

    for index in range(6):
        session.add_message(MessageSpeaker.COACH, f"Question {index + 1}", now)
        session.add_message(MessageSpeaker.CANDIDATE, f"Answer {index + 1}", now)

    assert session.question_count == 6
    assert not session.can_ask_another_question
    with pytest.raises(ValueError, match="cannot exceed 6"):
        session.add_message(MessageSpeaker.COACH, "Question 7", now)


def test_session_rejects_messages_after_completion() -> None:
    session = build_session()
    session.status = InterviewSessionStatus.COMPLETED

    with pytest.raises(ValueError, match="active interview session"):
        session.add_message(MessageSpeaker.CANDIDATE, "Late answer", datetime.now(timezone.utc))
