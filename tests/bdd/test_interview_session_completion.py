from pathlib import Path

from pytest_bdd import given, scenarios, then, when

scenarios(str(Path(__file__).parent / "features" / "interview_session_completion.feature"))


@given("the candidate closed the browser tab without finishing")
def closed_tab():
    pass  # no existe endpoint/evento que marque la sesión como abandonada


@when("the candidate opens the interview history")
def open_history():
    pass


@then("the session has a completion date")
def completion_date(response):
    assert response.json()["completed_at"] is not None


@then("the session has 6 questions and the last message is from the candidate")
def six_questions(ctx):
    session = ctx["session"]
    assert session["question_count"] == session["max_questions"] == 6
    assert session["messages"][-1]["speaker"] == "candidate"
    assert session["status"] == "active"
