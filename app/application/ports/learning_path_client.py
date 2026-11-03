from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LearningPathProgress:
    learning_path_id: int
    job_id: int
    progress_percentage: int
    completed_skills: list[str]


class LearningPathClient(ABC):
    @abstractmethod
    async def get_progress_by_job(self, user_id: int, job_id: int) -> LearningPathProgress: ...
