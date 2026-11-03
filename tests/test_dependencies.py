import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.dependencies import get_current_user_id
from app.infrastructure.configuration.settings import get_settings


def make_request(headers: list[tuple[bytes, bytes]]) -> Request:
    return Request({"type": "http", "method": "GET", "path": "/", "headers": headers})


def test_current_user_id_uses_configured_gateway_header(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@localhost:5432/interview_coach_db")
    monkeypatch.setenv("IDENTITY_SERVICE_URL", "http://identity")
    monkeypatch.setenv("JOB_DISCOVERY_SERVICE_URL", "http://jobs")
    monkeypatch.setenv("GAP_ANALYSIS_SERVICE_URL", "http://gaps")
    monkeypatch.setenv("LEARNING_PATHWAY_SERVICE_URL", "http://paths")
    monkeypatch.setenv("GATEWAY_USER_ID_HEADER", "X-User-Id")
    monkeypatch.setenv("INTERNAL_API_KEY", "test-key")
    get_settings.cache_clear()

    assert get_current_user_id(make_request([(b"x-user-id", b"42")])) == 42


def test_current_user_id_rejects_missing_or_invalid_header(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@localhost:5432/interview_coach_db")
    monkeypatch.setenv("IDENTITY_SERVICE_URL", "http://identity")
    monkeypatch.setenv("JOB_DISCOVERY_SERVICE_URL", "http://jobs")
    monkeypatch.setenv("GAP_ANALYSIS_SERVICE_URL", "http://gaps")
    monkeypatch.setenv("LEARNING_PATHWAY_SERVICE_URL", "http://paths")
    monkeypatch.setenv("GATEWAY_USER_ID_HEADER", "X-User-Id")
    monkeypatch.setenv("INTERNAL_API_KEY", "test-key")
    get_settings.cache_clear()

    for request in (make_request([]), make_request([(b"x-user-id", b"zero")]), make_request([(b"x-user-id", b"0")])):
        with pytest.raises(HTTPException) as error:
            get_current_user_id(request)
        assert error.value.status_code == 401
