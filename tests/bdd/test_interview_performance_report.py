from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then

scenarios(str(Path(__file__).parent / "features" / "interview_performance_report.feature"))


@given("the AI interview provider is unavailable")
def llm_down(world):
    world.llm.down = True


@then(parsers.re(r"the report contains technical (?P<t>\d+), behavioral (?P<b>\d+), communication (?P<c>\d+) "
                 r"and overall (?P<o>\d+) scores"))
def scores(response, t, b, c, o):
    report = response.json()["report"]
    assert (report["technical_score"], report["behavioral_score"], report["communication_score"],
            report["overall_score"]) == (int(t), int(b), int(c), int(o))


@then("the report lists strengths, improvement areas and recommendations")
def report_lists(response):
    report = response.json()["report"]
    assert report["strengths"] and report["improvement_areas"] and report["recommendations"]


@then("the AI evaluated the full transcript of the session")
def full_transcript(world, response):
    evaluated = world.llm.contexts[-1].transcript
    assert len(evaluated) == len(response.json()["messages"]) == 7  # 4 preguntas + 3 respuestas


@then(parsers.re(r'the interview session remains "(?P<status>[^"]+)"'))
def remains(world, ctx, status):
    assert world.sessions.sessions[ctx["session"]["id"]].status.value == status
