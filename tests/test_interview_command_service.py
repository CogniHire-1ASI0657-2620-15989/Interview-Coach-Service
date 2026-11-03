import asyncio
from datetime import datetime, timezone

import pytest

from app.application.internal.command_services.default_interview_command_service import DefaultInterviewCommandService
from app.application.ports.favorite_job_client import FavoriteJob
from app.application.ports.gap_analysis_client import GapAnalysisReport, MissingSkill
from app.application.ports.identity_profile_client import CandidateProfile
from app.application.ports.interview_llm_client import InterviewEvaluation
from app.application.ports.learning_path_client import LearningPathProgress
from app.domain.model.commands.complete_interview_command import CompleteInterviewCommand
from app.domain.model.commands.start_interview_command import StartInterviewCommand
from app.domain.model.commands.submit_interview_response_command import SubmitInterviewResponseCommand
from app.domain.model.value_objects.interview_mode import InterviewMode


class InMemoryInterviewSessionRepository:
    def __init__(self):
        self.session = None

    async def upsert(self, session):
        session.id = session.id or 1
        for message in session.messages:
            message.id = message.id or message.sequence
            message.session_id = session.id
        if session.report:
            session.report.id = session.report.id or 1
            session.report.session_id = session.id
        self.session = session
        return session

    async def find_by_id_and_user(self, session_id, user_id):
        if self.session and self.session.id == session_id and self.session.user_id == user_id:
            return self.session
        return None

    async def list_by_user(self, user_id):
        return [self.session] if self.session and self.session.user_id == user_id else []


class FakeProfileClient:
    async def get_profile(self, user_id):
        return CandidateProfile(
            user_id=user_id,
            name="Ana",
            segment="practicante",
            target_position="Backend Developer",
            hard_skills=["Python"],
            soft_skills=["Comunicación"],
            professional_summary="Proyecto universitario con FastAPI.",
        )


class FakeFavoriteJobClient:
    async def get_favorite_job(self, user_id, job_id):
        return FavoriteJob(id=job_id, title="Backend Developer", description="Construir APIs con Python y PostgreSQL.")


class FakeGapAnalysisClient:
    async def get_report(self, user_id, job_id):
        return GapAnalysisReport(
            job_id=job_id,
            missing_hard_skills=[MissingSkill(name="PostgreSQL", skill_type="hard")],
            missing_soft_skills=[],
        )


class FakeLearningPathClient:
    async def get_progress_by_job(self, user_id, job_id):
        return LearningPathProgress(
            learning_path_id=1,
            job_id=job_id,
            progress_percentage=25,
            completed_skills=["Python"],
        )


class FakeInterviewLlmClient:
    def __init__(self):
        self.question_contexts = []

    async def generate_question(self, context):
        self.question_contexts.append(context)
        return f"Pregunta {context.question_number}: ¿Cómo aplicarías Python en este puesto?"

    async def evaluate(self, context):
        return InterviewEvaluation(
            technical_score=80,
            behavioral_score=75,
            communication_score=85,
            overall_score=80,
            strengths=["Explica con claridad su proyecto."],
            improvement_areas=["Profundizar en PostgreSQL."],
            recommendations=["Practica consultas e índices en PostgreSQL."],
        )


def build_service():
    repository = InMemoryInterviewSessionRepository()
    llm = FakeInterviewLlmClient()
    commits = []

    async def commit():
        commits.append(datetime.now(timezone.utc))

    return (
        DefaultInterviewCommandService(
            repository=repository,
            profile_client=FakeProfileClient(),
            favorite_job_client=FakeFavoriteJobClient(),
            gap_analysis_client=FakeGapAnalysisClient(),
            learning_path_client=FakeLearningPathClient(),
            llm_client=llm,
            commit=commit,
        ),
        llm,
        commits,
    )


def test_full_interview_flow_stops_at_six_questions_and_generates_report() -> None:
    async def scenario():
        service, llm, commits = build_service()
        interview = await service.handle_start(StartInterviewCommand(user_id=7, job_id=9, mode=InterviewMode.MIXED))

        for number in range(1, 7):
            interview = await service.handle_submit_response(
                SubmitInterviewResponseCommand(user_id=7, session_id=interview.id, content=f"Respuesta {number}")
            )

        completed = await service.handle_complete(CompleteInterviewCommand(user_id=7, session_id=interview.id))
        return completed, llm, commits

    interview, llm, commits = asyncio.run(scenario())

    assert interview.question_count == 6
    assert len([message for message in interview.messages if message.speaker.value == "coach"]) == 6
    assert len([message for message in interview.messages if message.speaker.value == "candidate"]) == 6
    assert interview.status.value == "completed"
    assert interview.report is not None
    assert interview.report.overall_score == 80
    assert llm.question_contexts[0].job_title == "Backend Developer"
    assert llm.question_contexts[0].job_description == "Construir APIs con Python y PostgreSQL."
    assert llm.question_contexts[0].missing_hard_skills == ["PostgreSQL"]
    assert len(commits) == 13


def test_submit_response_rejects_another_user_session() -> None:
    async def scenario():
        service, _, _ = build_service()
        interview = await service.handle_start(StartInterviewCommand(user_id=7, job_id=9, mode=InterviewMode.MIXED))
        await service.handle_submit_response(
            SubmitInterviewResponseCommand(user_id=8, session_id=interview.id, content="Intento no autorizado")
        )

    with pytest.raises(ValueError, match="not found"):
        asyncio.run(scenario())
