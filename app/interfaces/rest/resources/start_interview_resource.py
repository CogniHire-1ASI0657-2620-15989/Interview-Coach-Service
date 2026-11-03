from pydantic import BaseModel, Field

from app.domain.model.value_objects.interview_mode import InterviewMode


class StartInterviewResource(BaseModel):
    job_id: int = Field(gt=0)
    mode: InterviewMode = InterviewMode.MIXED
