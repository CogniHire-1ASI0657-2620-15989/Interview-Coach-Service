from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.model.aggregates.interview_session import InterviewSession
from app.domain.model.entities.interview_report import InterviewReport
from app.domain.model.entities.transcript_message import TranscriptMessage
from app.domain.model.value_objects.interview_mode import InterviewMode
from app.domain.model.value_objects.interview_session_status import InterviewSessionStatus
from app.domain.model.value_objects.message_speaker import MessageSpeaker
from app.domain.repositories.interview_session_repository import InterviewSessionRepository
from app.infrastructure.persistence.sqlalchemy.models.interview_session_model import (
    InterviewReportModel,
    InterviewSessionModel,
    TranscriptMessageModel,
)


class SQLAlchemyInterviewSessionRepository(InterviewSessionRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert(self, session: InterviewSession) -> InterviewSession:
        model = await self._get_model_by_id(session.id) if session.id is not None else None
        if model is None:
            model = InterviewSessionModel(user_id=session.user_id, job_id=session.job_id)
            self._session.add(model)
        self._copy_to_model(session, model)
        await self._session.flush()
        await self._session.refresh(model, attribute_names=["messages", "report"])
        return self._to_entity(model)

    async def find_by_id_and_user(self, session_id: int, user_id: int) -> InterviewSession | None:
        result = await self._session.execute(
            self._with_relations().where(InterviewSessionModel.id == session_id, InterviewSessionModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_user(self, user_id: int) -> list[InterviewSession]:
        result = await self._session.execute(
            self._with_relations().where(InterviewSessionModel.user_id == user_id).order_by(InterviewSessionModel.created_at.desc())
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    async def _get_model_by_id(self, session_id: int) -> InterviewSessionModel | None:
        result = await self._session.execute(self._with_relations().where(InterviewSessionModel.id == session_id))
        return result.scalar_one_or_none()

    @staticmethod
    def _with_relations():
        return select(InterviewSessionModel).options(
            selectinload(InterviewSessionModel.messages),
            selectinload(InterviewSessionModel.report),
        )

    @staticmethod
    def _copy_to_model(session: InterviewSession, model: InterviewSessionModel) -> None:
        model.user_id = session.user_id
        model.job_id = session.job_id
        model.job_title = session.job_title
        model.job_description = session.job_description
        model.user_segment = session.user_segment
        model.mode = session.mode.value
        model.status = session.status.value
        model.question_count = session.question_count
        model.created_at = session.created_at
        model.updated_at = session.updated_at
        model.completed_at = session.completed_at

        persisted_messages: list[TranscriptMessageModel] = []
        existing_messages = {message.id: message for message in model.messages if message.id is not None}
        for message in session.messages:
            message_model = existing_messages.get(message.id) if message.id is not None else None
            if message_model is None:
                message_model = TranscriptMessageModel()
            message_model.sequence = message.sequence
            message_model.speaker = message.speaker.value
            message_model.content = message.content
            message_model.created_at = message.created_at
            persisted_messages.append(message_model)
        model.messages[:] = persisted_messages

        if session.report is None:
            model.report = None
        else:
            report_model = model.report or InterviewReportModel()
            report_model.technical_score = session.report.technical_score
            report_model.behavioral_score = session.report.behavioral_score
            report_model.communication_score = session.report.communication_score
            report_model.overall_score = session.report.overall_score
            report_model.strengths = session.report.strengths
            report_model.improvement_areas = session.report.improvement_areas
            report_model.recommendations = session.report.recommendations
            report_model.generated_at = session.report.generated_at
            model.report = report_model

    @staticmethod
    def _to_entity(model: InterviewSessionModel) -> InterviewSession:
        return InterviewSession(
            id=model.id,
            user_id=model.user_id,
            job_id=model.job_id,
            job_title=model.job_title,
            job_description=model.job_description,
            user_segment=model.user_segment,
            mode=InterviewMode(model.mode),
            status=InterviewSessionStatus(model.status),
            question_count=model.question_count,
            created_at=model.created_at,
            updated_at=model.updated_at,
            completed_at=model.completed_at,
            messages=[
                TranscriptMessage(
                    id=message.id,
                    session_id=message.session_id,
                    sequence=message.sequence,
                    speaker=MessageSpeaker(message.speaker),
                    content=message.content,
                    created_at=message.created_at,
                )
                for message in model.messages
            ],
            report=(
                InterviewReport(
                    id=model.report.id,
                    session_id=model.report.session_id,
                    technical_score=model.report.technical_score,
                    behavioral_score=model.report.behavioral_score,
                    communication_score=model.report.communication_score,
                    overall_score=model.report.overall_score,
                    strengths=list(model.report.strengths),
                    improvement_areas=list(model.report.improvement_areas),
                    recommendations=list(model.report.recommendations),
                    generated_at=model.report.generated_at,
                )
                if model.report
                else None
            ),
        )
