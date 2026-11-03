import asyncio
from datetime import datetime, timezone

from app.application.ports.favorite_job_client import FavoriteJob, FavoriteJobClient
from app.application.ports.gap_analysis_client import GapAnalysisClient, GapAnalysisReport
from app.application.ports.identity_profile_client import CandidateProfile, IdentityProfileClient
from app.application.ports.interview_llm_client import InterviewEvaluation, InterviewLlmClient, InterviewPromptContext
from app.application.ports.learning_path_client import LearningPathClient, LearningPathProgress
from app.domain.model.aggregates.interview_session import InterviewSession
from app.domain.model.commands.complete_interview_command import CompleteInterviewCommand
from app.domain.model.commands.start_interview_command import StartInterviewCommand
from app.domain.model.commands.submit_interview_response_command import SubmitInterviewResponseCommand
from app.domain.model.entities.interview_report import InterviewReport
from app.domain.model.value_objects.interview_session_status import InterviewSessionStatus
from app.domain.model.value_objects.message_speaker import MessageSpeaker
from app.domain.repositories.interview_session_repository import InterviewSessionRepository
from app.domain.services.interview_command_service import InterviewCommandService


class DefaultInterviewCommandService(InterviewCommandService):
    def __init__(
        self,
        repository: InterviewSessionRepository,
        profile_client: IdentityProfileClient,
        favorite_job_client: FavoriteJobClient,
        gap_analysis_client: GapAnalysisClient,
        learning_path_client: LearningPathClient,
        llm_client: InterviewLlmClient,
        commit,
    ):
        self._repository = repository
        self._profile_client = profile_client
        self._favorite_job_client = favorite_job_client
        self._gap_analysis_client = gap_analysis_client
        self._learning_path_client = learning_path_client
        self._llm_client = llm_client
        self._commit = commit

    async def handle_start(self, command: StartInterviewCommand) -> InterviewSession:
        profile, job = await asyncio.gather(
            self._profile_client.get_profile(command.user_id),
            self._favorite_job_client.get_favorite_job(command.user_id, command.job_id),
        )
        now = datetime.now(timezone.utc)
        session = InterviewSession(
            id=None,
            user_id=command.user_id,
            job_id=job.id,
            job_title=job.title,
            job_description=job.description,
            user_segment=profile.segment,
            mode=command.mode,
            status=InterviewSessionStatus.ACTIVE,
            question_count=0,
            created_at=now,
            updated_at=now,
        )
        prompt_context = await self._build_prompt_context(session, profile=profile, job=job)
        session.add_message(MessageSpeaker.COACH, await self._llm_client.generate_question(prompt_context), now)
        saved = await self._repository.upsert(session)
        await self._commit()
        return saved

    async def handle_submit_response(self, command: SubmitInterviewResponseCommand) -> InterviewSession:
        session = await self._get_active_session(command.session_id, command.user_id)
        now = datetime.now(timezone.utc)
        session.add_message(MessageSpeaker.CANDIDATE, command.content, now)
        saved = await self._repository.upsert(session)
        await self._commit()

        if not saved.can_ask_another_question:
            return saved

        prompt_context = await self._build_prompt_context(saved)
        saved.add_message(MessageSpeaker.COACH, await self._llm_client.generate_question(prompt_context), datetime.now(timezone.utc))
        saved = await self._repository.upsert(saved)
        await self._commit()
        return saved

    async def handle_complete(self, command: CompleteInterviewCommand) -> InterviewSession:
        session = await self._get_active_session(command.session_id, command.user_id)
        prompt_context = await self._build_prompt_context(session)
        evaluation = await self._llm_client.evaluate(prompt_context)
        completed_at = datetime.now(timezone.utc)
        session.complete(self._to_report(evaluation, session.id, completed_at), completed_at)
        saved = await self._repository.upsert(session)
        await self._commit()
        return saved

    async def _get_active_session(self, session_id: int, user_id: int) -> InterviewSession:
        session = await self._repository.find_by_id_and_user(session_id, user_id)
        if session is None:
            raise ValueError("Interview session not found.")
        if session.status != InterviewSessionStatus.ACTIVE:
            raise ValueError("Interview session is no longer active.")
        return session

    async def _build_prompt_context(
        self,
        session: InterviewSession,
        *,
        profile: CandidateProfile | None = None,
        job: FavoriteJob | None = None,
    ) -> InterviewPromptContext:
        if profile is None or job is None:
            profile, job = await asyncio.gather(
                self._profile_client.get_profile(session.user_id),
                self._favorite_job_client.get_favorite_job(session.user_id, session.job_id),
            )

        gap_result, path_result = await asyncio.gather(
            self._gap_analysis_client.get_report(session.user_id, session.job_id),
            self._learning_path_client.get_progress_by_job(session.user_id, session.job_id),
            return_exceptions=True,
        )
        gap_report = gap_result if isinstance(gap_result, GapAnalysisReport) else None
        learning_path = path_result if isinstance(path_result, LearningPathProgress) else None
        question_number = session.question_count + 1
        return InterviewPromptContext(
            candidate_name=profile.name,
            user_segment=profile.segment,
            target_position=profile.target_position,
            job_title=job.title,
            job_description=job.description,
            hard_skills=profile.hard_skills,
            soft_skills=profile.soft_skills,
            professional_summary=profile.professional_summary,
            missing_hard_skills=[skill.name for skill in gap_report.missing_hard_skills] if gap_report else [],
            missing_soft_skills=[skill.name for skill in gap_report.missing_soft_skills] if gap_report else [],
            completed_skills=learning_path.completed_skills if learning_path else [],
            mode=session.mode.value,
            question_number=question_number,
            question_kind=self._question_kind(question_number, session.mode.value),
            transcript=[(message.speaker.value, message.content) for message in session.messages],
        )

    @staticmethod
    def _question_kind(question_number: int, mode: str) -> str:
        if question_number == 1:
            return "general"
        if question_number == 2:
            return "behavioral"
        if mode == "behavioral" and question_number in (4, 5):
            return "behavioral"
        return "technical"

    @staticmethod
    def _to_report(evaluation: InterviewEvaluation, session_id: int | None, generated_at: datetime) -> InterviewReport:
        return InterviewReport(
            id=None,
            session_id=session_id,
            technical_score=evaluation.technical_score,
            behavioral_score=evaluation.behavioral_score,
            communication_score=evaluation.communication_score,
            overall_score=evaluation.overall_score,
            strengths=evaluation.strengths,
            improvement_areas=evaluation.improvement_areas,
            recommendations=evaluation.recommendations,
            generated_at=generated_at,
        )
