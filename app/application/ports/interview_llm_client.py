from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class InterviewPromptContext:
    candidate_name: str
    user_segment: str
    target_position: str | None
    job_title: str
    job_description: str | None
    hard_skills: list[str]
    soft_skills: list[str]
    professional_summary: str | None
    missing_hard_skills: list[str]
    missing_soft_skills: list[str]
    completed_skills: list[str]
    mode: str
    question_number: int
    question_kind: str
    transcript: list[tuple[str, str]]


@dataclass(frozen=True)
class InterviewEvaluation:
    technical_score: int
    behavioral_score: int
    communication_score: int
    overall_score: int
    strengths: list[str]
    improvement_areas: list[str]
    recommendations: list[str]


class LlmUnavailable(RuntimeError):
    """Raised when the configured LLM cannot produce a valid response."""


class InterviewLlmClient(ABC):
    @abstractmethod
    async def generate_question(self, context: InterviewPromptContext) -> str: ...

    @abstractmethod
    async def evaluate(self, context: InterviewPromptContext) -> InterviewEvaluation: ...
