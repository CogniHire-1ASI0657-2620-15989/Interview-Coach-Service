from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when

from conftest import headers

scenarios(str(Path(__file__).parent / "features" / "interview_text_conversation.feature"))


@given("the AI interview provider is unavailable")
def llm_down(world):
    world.llm.down = True


@when(parsers.re(r'the candidate opens the session at "(?P<path>[^"]+)"'), target_fixture="response")
def open_session(client, ctx, path):
    return client.get(path.format(id=ctx["session"]["id"]), headers=headers())


@then(parsers.re(r'the transcript shows "(?P<speakers>[^"]+)" in that order'))
def transcript_order(response, speakers):
    assert [m["speaker"] for m in response.json()["messages"]] == [s.strip() for s in speakers.split(",")]


@then(parsers.re(r"the question count is (?P<count>\d+)"))
def question_count(response, count):
    assert response.json()["question_count"] == int(count)


@then("the transcript messages are numbered consecutively")
def consecutive(response):
    sequences = [m["sequence"] for m in response.json()["messages"]]
    assert sequences == list(range(1, len(sequences) + 1))


@then("the candidate answer is kept in the transcript")
def answer_kept(world, ctx):
    session = world.sessions.sessions[ctx["session"]["id"]]
    assert [m.speaker.value for m in session.messages] == ["coach", "candidate"]
