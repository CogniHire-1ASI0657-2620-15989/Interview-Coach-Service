from abc import ABC, abstractmethod

from app.domain.model.aggregates.interview_session import InterviewSession


class InterviewSessionRepository(ABC):
    @abstractmethod
    async def upsert(self, session: InterviewSession) -> InterviewSession: ...

    @abstractmethod
    async def find_by_id_and_user(self, session_id: int, user_id: int) -> InterviewSession | None: ...

    @abstractmethod
    async def list_by_user(self, user_id: int) -> list[InterviewSession]: ...
