from pathlib import Path

from pytest_bdd import parsers, scenarios, then, when

from conftest import headers

scenarios(str(Path(__file__).parent / "features" / "interview_history.feature"))


@when(parsers.re(r'a GET request is sent to "(?P<path>/api/v1/interview-sessions)"'), target_fixture="response")
def list_sessions(client, path):
    return client.get(path, headers=headers())


@when(parsers.re(r'another candidate requests the session at "(?P<path>[^"]+)"'), target_fixture="response")
def other_candidate(client, ctx, path):
    return client.get(path.format(id=ctx["session"]["id"]), headers=headers(999))


@then(parsers.re(r'the history contains (?P<count>\d+) interviews? for "(?P<title>[^"]+)" '
                 r'with overall score (?P<score>\d+) and a date'))
def history(response, count, title, score):
    items = response.json()
    assert len(items) == int(count)
    assert items[0]["job_title"] == title and items[0]["overall_score"] == int(score)
    assert items[0]["created_at"] and items[0]["completed_at"]


@then("the history is empty")
def empty(response):
    assert response.json() == []
