from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class MissingSkill:
    name: str
    skill_type: str


@dataclass(frozen=True)
class GapAnalysisReport:
    job_id: int
    missing_hard_skills: list[MissingSkill]
    missing_soft_skills: list[MissingSkill]


class GapAnalysisClient(ABC):
    @abstractmethod
    async def get_report(self, user_id: int, job_id: int) -> GapAnalysisReport: ...
