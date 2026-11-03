from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.internal.command_services.default_interview_command_service import DefaultInterviewCommandService
from app.application.internal.query_service.default_interview_query_service import DefaultInterviewQueryService
from app.application.ports.interview_llm_client import LlmUnavailable
from app.dependencies import (
    get_current_user_id,
    get_db_session,
    get_interview_command_service,
    get_interview_query_service,
)
from app.domain.model.commands.complete_interview_command import CompleteInterviewCommand
from app.domain.model.queries.get_interview_session_query import GetInterviewSessionQuery
from app.domain.model.queries.list_interview_sessions_query import ListInterviewSessionsQuery
from app.interfaces.rest.resources.interview_session_resource import InterviewSessionResource, InterviewSessionSummaryResource
from app.interfaces.rest.resources.start_interview_resource import StartInterviewResource
from app.interfaces.rest.resources.submit_interview_response_resource import SubmitInterviewResponseResource
from app.interfaces.rest.transform.interview_session_resource_from_entity_assembler import InterviewSessionResourceFromEntityAssembler
from app.interfaces.rest.transform.start_interview_command_from_resource_assembler import StartInterviewCommandFromResourceAssembler
from app.interfaces.rest.transform.submit_interview_response_command_from_resource_assembler import (
    SubmitInterviewResponseCommandFromResourceAssembler,
)


router = APIRouter(prefix="/api/v1/interview-sessions", tags=["Interview Coach"])


@router.post("", response_model=InterviewSessionResource, status_code=status.HTTP_201_CREATED)
async def start_interview(
    resource: StartInterviewResource,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> InterviewSessionResource:
    service: DefaultInterviewCommandService = get_interview_command_service(session)
    try:
        interview_session = await service.handle_start(StartInterviewCommandFromResourceAssembler.to_command(user_id, resource))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (RuntimeError, LlmUnavailable) as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return InterviewSessionResourceFromEntityAssembler.to_resource(interview_session)


@router.post("/{session_id}/messages", response_model=InterviewSessionResource)
async def submit_response(
    session_id: int,
    resource: SubmitInterviewResponseResource,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> InterviewSessionResource:
    service: DefaultInterviewCommandService = get_interview_command_service(session)
    try:
        interview_session = await service.handle_submit_response(
            SubmitInterviewResponseCommandFromResourceAssembler.to_command(user_id, session_id, resource)
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except (RuntimeError, LlmUnavailable) as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return InterviewSessionResourceFromEntityAssembler.to_resource(interview_session)


@router.post("/{session_id}/complete", response_model=InterviewSessionResource)
async def complete_interview(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> InterviewSessionResource:
    service: DefaultInterviewCommandService = get_interview_command_service(session)
    try:
        interview_session = await service.handle_complete(CompleteInterviewCommand(user_id=user_id, session_id=session_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except (RuntimeError, LlmUnavailable) as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return InterviewSessionResourceFromEntityAssembler.to_resource(interview_session)


@router.get("", response_model=list[InterviewSessionSummaryResource])
async def list_interview_sessions(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> list[InterviewSessionSummaryResource]:
    service: DefaultInterviewQueryService = get_interview_query_service(session)
    sessions = await service.handle_list_by_user(ListInterviewSessionsQuery(user_id=user_id))
    return [InterviewSessionResourceFromEntityAssembler.to_summary_resource(item) for item in sessions]


@router.get("/{session_id}", response_model=InterviewSessionResource)
async def get_interview_session(
    session_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> InterviewSessionResource:
    service: DefaultInterviewQueryService = get_interview_query_service(session)
    interview_session = await service.handle_get_by_id(GetInterviewSessionQuery(user_id=user_id, session_id=session_id))
    if interview_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview session not found.")
    return InterviewSessionResourceFromEntityAssembler.to_resource(interview_session)
