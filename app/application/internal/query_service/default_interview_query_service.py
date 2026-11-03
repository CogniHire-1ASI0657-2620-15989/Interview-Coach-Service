from app.domain.model.aggregates.interview_session import InterviewSession
from app.domain.model.queries.get_interview_session_query import GetInterviewSessionQuery
from app.domain.model.queries.list_interview_sessions_query import ListInterviewSessionsQuery
from app.domain.repositories.interview_session_repository import InterviewSessionRepository
from app.domain.services.interview_query_service import InterviewQueryService


class DefaultInterviewQueryService(InterviewQueryService):
    def __init__(self, repository: InterviewSessionRepository):
        self._repository = repository

    async def handle_get_by_id(self, query: GetInterviewSessionQuery) -> InterviewSession | None:
        return await self._repository.find_by_id_and_user(query.session_id, query.user_id)

    async def handle_list_by_user(self, query: ListInterviewSessionsQuery) -> list[InterviewSession]:
        return await self._repository.list_by_user(query.user_id)
