import logging
from unittest.mock import patch

import pytest

from guestbook.app import create_app


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "guestbook.sqlite3")


@pytest.fixture
def app(db_path):
    return create_app(db_path=db_path)


@pytest.fixture
def client(app):
    return app.test_client()


class TestHealthzHappyPath:
    def test_get_returns_200_with_correct_json(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.content_type == "application/json"
        data = response.get_json()
        assert set(data.keys()) == {"status", "version", "uptimeSeconds"}
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"
        assert isinstance(data["uptimeSeconds"], int)
        assert data["uptimeSeconds"] >= 0

    def test_cache_control_no_store(self, client):
        response = client.get("/healthz")
        assert response.headers["Cache-Control"] == "no-store"


class TestHealthzUptime:
    def test_uptime_reflects_elapsed_time(self, client):
        with patch("guestbook.app.time") as mock_time:
            mock_time.monotonic.return_value = 1042.7
            with patch("guestbook.app._START", 1000.0):
                response = client.get("/healthz")
        data = response.get_json()
        assert data["uptimeSeconds"] == 42


class TestHealthzMethodNotAllowed:
    def test_post_returns_405(self, client):
        assert client.post("/healthz").status_code == 405

    def test_put_returns_405(self, client):
        assert client.put("/healthz").status_code == 405


class TestHealthzLogging:
    def test_no_info_log_for_healthz(self, client, caplog):
        with caplog.at_level(logging.DEBUG):
            client.get("/healthz")
        info_or_above = [r for r in caplog.records if r.levelno >= logging.INFO]
        healthz_logs = [r for r in info_or_above if "/healthz" in r.getMessage()]
        assert healthz_logs == []
