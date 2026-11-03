from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class FavoriteJob:
    id: int
    title: str
    description: str | None


class FavoriteJobClient(ABC):
    @abstractmethod
    async def get_favorite_job(self, user_id: int, job_id: int) -> FavoriteJob: ...
