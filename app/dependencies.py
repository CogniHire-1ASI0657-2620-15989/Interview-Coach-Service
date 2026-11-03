from collections.abc import AsyncGenerator

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.internal.command_services.default_interview_command_service import DefaultInterviewCommandService
from app.application.internal.query_service.default_interview_query_service import DefaultInterviewQueryService
from app.infrastructure.clients.gap_analysis_service_client import GapAnalysisServiceClient
from app.infrastructure.clients.groq_interview_llm_client import GroqInterviewLlmClient
from app.infrastructure.clients.identity_service_client import IdentityServiceClient
from app.infrastructure.clients.job_discovery_service_client import JobDiscoveryServiceClient
from app.infrastructure.clients.learning_pathway_service_client import LearningPathwayServiceClient
from app.infrastructure.configuration.settings import get_settings
from app.infrastructure.persistence.sqlalchemy.database import get_session
from app.infrastructure.persistence.sqlalchemy.repositories.sqlalchemy_interview_session_repository import (
    SQLAlchemyInterviewSessionRepository,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


def get_current_user_id(request: Request) -> int:
    header = get_settings().gateway_user_id_header
    raw_user_id = request.headers.get(header)
    if raw_user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Missing gateway identity header: {header}")
    try:
        user_id = int(raw_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid gateway user identifier.") from exc
    if user_id <= 0:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid gateway user identifier.")
    return user_id


def get_interview_command_service(session: AsyncSession) -> DefaultInterviewCommandService:
    settings = get_settings()
    if not settings.interview_groq_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="INTERVIEW_GROQ_API_KEY is not configured.",
        )
    return DefaultInterviewCommandService(
        repository=SQLAlchemyInterviewSessionRepository(session),
        profile_client=IdentityServiceClient(settings.identity_service_url, settings.internal_api_key),
        favorite_job_client=JobDiscoveryServiceClient(
            settings.job_discovery_service_url,
            settings.gateway_user_id_header,
            settings.internal_api_key,
        ),
        gap_analysis_client=GapAnalysisServiceClient(
            settings.gap_analysis_service_url,
            settings.gateway_user_id_header,
            settings.internal_api_key,
        ),
        learning_path_client=LearningPathwayServiceClient(
            settings.learning_pathway_service_url,
            settings.gateway_user_id_header,
            settings.internal_api_key,
        ),
        llm_client=GroqInterviewLlmClient(settings.interview_groq_api_key, settings.interview_groq_model),
        commit=session.commit,
    )


def get_interview_query_service(session: AsyncSession) -> DefaultInterviewQueryService:
    return DefaultInterviewQueryService(SQLAlchemyInterviewSessionRepository(session))
