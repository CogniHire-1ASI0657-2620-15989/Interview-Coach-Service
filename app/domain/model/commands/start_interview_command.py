from dataclasses import dataclass

from app.domain.model.value_objects.interview_mode import InterviewMode


@dataclass(frozen=True)
class StartInterviewCommand:
    user_id: int
    job_id: int
    mode: InterviewMode
