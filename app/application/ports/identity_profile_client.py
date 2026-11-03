from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateProfile:
    user_id: int
    name: str
    segment: str
    target_position: str | None
    hard_skills: list[str]
    soft_skills: list[str]
    professional_summary: str | None


class IdentityProfileClient(ABC):
    @abstractmethod
    async def get_profile(self, user_id: int) -> CandidateProfile: ...
