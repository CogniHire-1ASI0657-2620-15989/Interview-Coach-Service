from app.domain.model.aggregates.interview_session import InterviewSession
from app.interfaces.rest.resources.interview_session_resource import (
    InterviewReportResource,
    InterviewSessionResource,
    InterviewSessionSummaryResource,
    TranscriptMessageResource,
)


class InterviewSessionResourceFromEntityAssembler:
    @staticmethod
    def to_resource(session: InterviewSession) -> InterviewSessionResource:
        return InterviewSessionResource(
            id=session.id,
            job_id=session.job_id,
            job_title=session.job_title,
            user_segment=session.user_segment,
            mode=session.mode.value,
            status=session.status.value,
            question_count=session.question_count,
            max_questions=session.MAX_QUESTIONS,
            created_at=session.created_at,
            updated_at=session.updated_at,
            completed_at=session.completed_at,
            messages=[
                TranscriptMessageResource(
                    id=message.id,
                    sequence=message.sequence,
                    speaker=message.speaker.value,
                    content=message.content,
                    created_at=message.created_at,
                )
                for message in session.messages
            ],
            report=(
                InterviewReportResource(
                    id=session.report.id,
                    technical_score=session.report.technical_score,
                    behavioral_score=session.report.behavioral_score,
                    communication_score=session.report.communication_score,
                    overall_score=session.report.overall_score,
                    strengths=session.report.strengths,
                    improvement_areas=session.report.improvement_areas,
                    recommendations=session.report.recommendations,
                    generated_at=session.report.generated_at,
                )
                if session.report
                else None
            ),
        )

    @staticmethod
    def to_summary_resource(session: InterviewSession) -> InterviewSessionSummaryResource:
        return InterviewSessionSummaryResource(
            id=session.id,
            job_id=session.job_id,
            job_title=session.job_title,
            mode=session.mode.value,
            status=session.status.value,
            question_count=session.question_count,
            created_at=session.created_at,
            completed_at=session.completed_at,
            overall_score=session.report.overall_score if session.report else None,
        )
