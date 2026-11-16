from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then

scenarios(str(Path(__file__).parent / "features" / "contextual_interview_questions.feature"))


@given(parsers.re(r'the gap report of job (?P<job>\d+) lists "(?P<skill>[^"]+)" as a missing skill'))
def gap_lists(world, job, skill):
    world.gap.missing_hard = [skill]


@given(parsers.re(r'the candidate completed the learning pathway course of "(?P<skill>[^"]+)"'))
def completed_course(world, skill):
    world.learning.completed = [skill]


@given("the Gap Analysis and Learning Pathway services are unavailable")
def context_down(world):
    world.gap.available = False
    world.learning.available = False


@then(parsers.re(r'the AI receives the job title "(?P<title>[^"]+)"'))
def receives_title(world, title):
    assert world.llm.contexts[-1].job_title == title


@then(parsers.re(r'the AI receives "(?P<skill>[^"]+)" as a completed skill'))
def receives_completed(world, skill):
    assert skill in world.llm.contexts[-1].completed_skills


@then(parsers.re(r'the AI receives "(?P<skill>[^"]+)" as a missing hard skill'))
def receives_missing(world, skill):
    assert skill in world.llm.contexts[-1].missing_hard_skills


@then("the AI receives no skill gaps nor completed courses")
def receives_nothing(world):
    context = world.llm.contexts[-1]
    assert context.missing_hard_skills == [] and context.completed_skills == []
