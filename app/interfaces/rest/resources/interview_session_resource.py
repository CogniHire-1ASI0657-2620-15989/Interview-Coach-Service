from datetime import datetime

from pydantic import BaseModel


class TranscriptMessageResource(BaseModel):
    id: int
    sequence: int
    speaker: str
    content: str
    created_at: datetime


class InterviewReportResource(BaseModel):
    id: int
    technical_score: int
    behavioral_score: int
    communication_score: int
    overall_score: int
    strengths: list[str]
    improvement_areas: list[str]
    recommendations: list[str]
    generated_at: datetime


class InterviewSessionResource(BaseModel):
    id: int
    job_id: int
    job_title: str
    user_segment: str
    mode: str
    status: str
    question_count: int
    max_questions: int
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    messages: list[TranscriptMessageResource]
    report: InterviewReportResource | None


class InterviewSessionSummaryResource(BaseModel):
    id: int
    job_id: int
    job_title: str
    mode: str
    status: str
    question_count: int
    created_at: datetime
    completed_at: datetime | None
    overall_score: int | None
