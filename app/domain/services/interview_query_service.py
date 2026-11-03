from abc import ABC, abstractmethod

from app.domain.model.aggregates.interview_session import InterviewSession
from app.domain.model.queries.get_interview_session_query import GetInterviewSessionQuery
from app.domain.model.queries.list_interview_sessions_query import ListInterviewSessionsQuery


class InterviewQueryService(ABC):
    @abstractmethod
    async def handle_get_by_id(self, query: GetInterviewSessionQuery) -> InterviewSession | None: ...

    @abstractmethod
    async def handle_list_by_user(self, query: ListInterviewSessionsQuery) -> list[InterviewSession]: ...
