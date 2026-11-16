"""Soporte común de los tests BDD del Interview Coach Service (ningún archivo de app/ se modifica).

El microservicio se prueba por su API HTTP real (/api/v1/interview-sessions) con el servicio de
aplicación y el agregado InterviewSession reales. Se sustituyen por fakes en memoria los puertos que
salen del proceso: Identity, Job Discovery (favoritos), Gap Analysis, Learning Pathway, el LLM (Groq)
y PostgreSQL. settings.py ejecuta load_dotenv(): las variables se fuerzan aquí para no usar el .env local.

Los escenarios con la etiqueta @pending describen criterios de aceptación del Sprint 3 que todavía
no tienen lógica en el backend; se recolectan pero se omiten (skip) con el motivo indicado.
"""
import os
from datetime import datetime, timezone
from types import SimpleNamespace

for key, value in {"DATABASE_URL": "postgresql+psycopg://test", "IDENTITY_SERVICE_URL": "http://identity.test",
                   "JOB_DISCOVERY_SERVICE_URL": "http://jobs.test", "GAP_ANALYSIS_SERVICE_URL": "http://gap.test",
                   "LEARNING_PATHWAY_SERVICE_URL": "http://learning.test", "GATEWAY_USER_ID_HEADER": "X-User-Id",
                   "INTERNAL_API_KEY": "test-key", "INTERVIEW_GROQ_API_KEY": ""}.items():
    os.environ[key] = value

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, then, when

from app.application.internal.command_services.default_interview_command_service import DefaultInterviewCommandService
from app.application.internal.query_service.default_interview_query_service import DefaultInterviewQueryService
from app.application.ports.favorite_job_client import FavoriteJob
from app.application.ports.gap_analysis_client import GapAnalysisReport, MissingSkill
from app.application.ports.identity_profile_client import CandidateProfile
from app.application.ports.interview_llm_client import InterviewEvaluation, LlmUnavailable
from app.application.ports.learning_path_client import LearningPathProgress
from app.dependencies import get_db_session
from app.interfaces.rest.controller import interview_session_controller as controller
from app.main import app

USER_ID = 101
JOB_ID = 50


def headers(user_id: int = USER_ID) -> dict:
    return {"X-User-Id": str(user_id), "X-Internal-Api-Key": "test-key"}


def pytest_bdd_apply_tag(tag, function):
    if tag == "pending":
        pytest.mark.skip(reason="Criterio de aceptación del Sprint 3 aún sin lógica en el backend")(function)
        return True
    return None


# ---------- Fakes de los puertos externos ----------
class FakeIdentity:
    async def get_profile(self, user_id):
        return CandidateProfile(user_id, "Ana Perez", "practicante", "Backend Developer", ["Python"],
                                ["Comunicación"], "Proyecto universitario con FastAPI.")


class FakeFavorites:
    def __init__(self):
        self.jobs: dict[tuple[int, int], FavoriteJob] = {}

    async def get_favorite_job(self, user_id, job_id):
        if (user_id, job_id) not in self.jobs:
            raise ValueError("The selected job is not in the user's favorites.")
        return self.jobs[(user_id, job_id)]


class FakeGap:
    def __init__(self):
        self.available = True
        self.missing_hard: list[str] = []

    async def get_report(self, user_id, job_id):
        if not self.available:
            raise RuntimeError("Gap Analysis Service is unavailable.")
        return GapAnalysisReport(job_id, [MissingSkill(s, "hard") for s in self.missing_hard], [])


class FakeLearningPath:
    def __init__(self):
        self.available = True
        self.completed: list[str] = []

    async def get_progress_by_job(self, user_id, job_id):
        if not self.available:
            raise RuntimeError("Learning Pathway Service is unavailable.")
        return LearningPathProgress(1, job_id, 100 if self.completed else 0, self.completed)


class FakeLlm:
    """Simula Groq: genera preguntas deterministas y guarda el contexto recibido en cada llamada."""

    def __init__(self):
        self.down = False
        self.contexts = []

    async def generate_question(self, context):
        if self.down:
            raise LlmUnavailable("Interview LLM is unavailable.")
        self.contexts.append(context)
        return f"Pregunta {context.question_number} ({context.question_kind}) sobre {context.job_title}"

    async def evaluate(self, context):
        if self.down:
            raise LlmUnavailable("Interview LLM is unavailable.")
        self.contexts.append(context)
        return InterviewEvaluation(78, 70, 82, 76, ["Explica con claridad sus proyectos"],
                                   ["Profundizar en Docker"], ["Practicar preguntas de contenedores"])


class FakeSessionRepo:
    def __init__(self):
        self.sessions = {}

    async def upsert(self, session):
        if session.id is None:
            session.id = len(self.sessions) + 1
        for message in session.messages:
            message.id = message.id or message.sequence
            message.session_id = session.id
        if session.report:
            session.report.id = session.report.id or session.id
            session.report.session_id = session.id
        self.sessions[session.id] = session
        return session

    async def find_by_id_and_user(self, session_id, user_id):
        session = self.sessions.get(session_id)
        return session if session and session.user_id == user_id else None

    async def list_by_user(self, user_id):
        return sorted((s for s in self.sessions.values() if s.user_id == user_id),
                      key=lambda s: s.created_at, reverse=True)


@pytest.fixture
def world():
    return SimpleNamespace(favorites=FakeFavorites(), gap=FakeGap(), learning=FakeLearningPath(), llm=FakeLlm(),
                           sessions=FakeSessionRepo())


@pytest.fixture
def ctx():
    return {}


@pytest.fixture
def client(world, monkeypatch):
    from app.infrastructure.configuration.settings import get_settings
    get_settings.cache_clear()

    async def commit(): ...

    async def fake_session():
        yield None

    app.dependency_overrides[get_db_session] = fake_session
    monkeypatch.setattr(controller, "get_interview_command_service",
                        lambda s: DefaultInterviewCommandService(world.sessions, FakeIdentity(), world.favorites,
                                                                 world.gap, world.learning, world.llm, commit))
    monkeypatch.setattr(controller, "get_interview_query_service",
                        lambda s: DefaultInterviewQueryService(world.sessions))
    yield TestClient(app)
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def start_session(client, job_id: int = JOB_ID, mode: str | None = None):
    payload = {"job_id": job_id} if mode is None else {"job_id": job_id, "mode": mode}
    return client.post("/api/v1/interview-sessions", json=payload, headers=headers())


# ---------- Steps compartidos ----------
@given(parsers.re(r'the candidate saved the job (?P<job>\d+) "(?P<title>[^"]+)" as favorite'))
def favorite_job(world, job, title):
    world.favorites.jobs[(USER_ID, int(job))] = FavoriteJob(int(job), title, f"Vacante de {title}")


@given(parsers.re(r"the candidate has an active interview session for job (?P<job>\d+)"))
def active_session(client, ctx, job):
    response = start_session(client, int(job))
    assert response.status_code == 201, response.text
    ctx["session"] = response.json()


@given(parsers.re(r"the candidate answered (?P<count>\d+) questions?"))
def answered(client, ctx, count):
    for n in range(int(count)):
        response = client.post(f"/api/v1/interview-sessions/{ctx['session']['id']}/messages",
                               json={"content": f"Respuesta {n + 1} con un ejemplo de mi proyecto"}, headers=headers())
        assert response.status_code == 200, response.text
        ctx["session"] = response.json()


@given("the candidate finished the interview session")
def finished(client, ctx):
    response = client.post(f"/api/v1/interview-sessions/{ctx['session']['id']}/complete", headers=headers())
    assert response.status_code == 200, response.text
    ctx["session"] = response.json()


@when(parsers.re(r'a POST request is sent to "/api/v1/interview-sessions" for job (?P<job>\d+) with mode "(?P<mode>[^"]+)"'),
      target_fixture="response")
def start_with_mode(client, job, mode):
    return start_session(client, int(job), mode)


@when(parsers.re(r'a POST request is sent to "/api/v1/interview-sessions" for job (?P<job>\d+) without a mode'),
      target_fixture="response")
def start_without_mode(client, job):
    return start_session(client, int(job))


@when(parsers.re(r'the candidate sends the answer "(?P<content>[^"]*)" to "(?P<path>[^"]+)"'), target_fixture="response")
def send_answer(client, ctx, content, path):
    return client.post(path.format(id=ctx["session"]["id"]), json={"content": content}, headers=headers())


@when(parsers.re(r'a POST request is sent to "(?P<path>/api/v1/interview-sessions/\{id\}/complete)"'),
      target_fixture="response")
def complete(client, ctx, path):
    return client.post(path.format(id=ctx["session"]["id"]), headers=headers())


@then(parsers.re(r"the response status is (?P<code>\d+) .+"))
def status_is(response, code):
    assert response.status_code == int(code), response.text


@then(parsers.re(r'the response body contains the message "(?P<message>[^"]+)"'))
def message_is(response, message):
    assert message in str(response.json().get("detail"))


@then(parsers.re(r'the session status is "(?P<status>[^"]+)"'))
def session_status(response, status):
    assert response.json()["status"] == status
