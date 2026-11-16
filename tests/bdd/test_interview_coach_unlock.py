from pathlib import Path

from pytest_bdd import given, parsers, scenarios

scenarios(str(Path(__file__).parent / "features" / "interview_coach_unlock.feature"))


@given(parsers.re(r"the learning pathway of job (?P<job>\d+) is (?P<pct>\d+)% completed"))
def pathway_progress(world, job, pct):
    world.learning.completed = ["Docker"] if int(pct) == 100 else []
