from pathlib import Path

from pytest_bdd import parsers, scenarios, then

from conftest import headers

scenarios(str(Path(__file__).parent / "features" / "interview_focus_configuration.feature"))


@then(parsers.re(r'the session mode is "(?P<mode>[^"]+)"'))
def session_mode(response, mode):
    assert response.json()["mode"] == mode


@then("the coach asks the first question")
def first_question(response):
    body = response.json()
    assert body["question_count"] == 1
    assert [m["speaker"] for m in body["messages"]] == ["coach"]


@then(parsers.re(r'the questions after the second one are "(?P<kind>[^"]+)" questions'))
def later_questions(client, world, response, kind):
    session_id = response.json()["id"]
    for n in range(3):
        client.post(f"/api/v1/interview-sessions/{session_id}/messages", json={"content": f"Respuesta {n}"},
                    headers=headers())
    kinds = [c.question_kind for c in world.llm.contexts]
    assert kinds[:2] == ["general", "behavioral"]
    assert set(kinds[2:]) == {kind}
