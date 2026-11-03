from app.application.internal.command_services.default_interview_command_service import DefaultInterviewCommandService


def test_question_plan_includes_general_behavioral_and_technical_questions() -> None:
    kinds = [DefaultInterviewCommandService._question_kind(number, "mixed") for number in range(1, 7)]

    assert kinds == ["general", "behavioral", "technical", "technical", "technical", "technical"]


def test_behavioral_mode_still_includes_technical_questions() -> None:
    kinds = [DefaultInterviewCommandService._question_kind(number, "behavioral") for number in range(1, 7)]

    assert kinds == ["general", "behavioral", "technical", "behavioral", "behavioral", "technical"]
