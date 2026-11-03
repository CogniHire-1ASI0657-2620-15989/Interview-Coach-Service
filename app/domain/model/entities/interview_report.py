from dataclasses import dataclass
from datetime import datetime


@dataclass
class InterviewReport:
    id: int | None
    session_id: int | None
    technical_score: int
    behavioral_score: int
    communication_score: int
    overall_score: int
    strengths: list[str]
    improvement_areas: list[str]
    recommendations: list[str]
    generated_at: datetime

    def __post_init__(self) -> None:
        for name, score in (
            ("technical_score", self.technical_score),
            ("behavioral_score", self.behavioral_score),
            ("communication_score", self.communication_score),
            ("overall_score", self.overall_score),
        ):
            if not 0 <= score <= 100:
                raise ValueError(f"{name} must be between 0 and 100.")
