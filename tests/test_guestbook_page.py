import time

import pytest

from guestbook.app import create_app
from guestbook.storage import insert_entry

GUESTBOOK_URL = "/guestbook"


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "guestbook.sqlite3")


@pytest.fixture
def app(db_path):
    return create_app(db_path=db_path)


@pytest.fixture
def client(app):
    return app.test_client()


def _insert(db_path, author="Ada", message="Hello", created_at="2026-01-15T10:00:00.000000Z"):
    return insert_entry(db_path, author, message, created_at)


def _html(response):
    return response.get_data(as_text=True)


class TestGuestbookPageDisplay:
    def test_get_shows_entries_newest_first(self, client, db_path):
        _insert(db_path, author="First", message="Msg1", created_at="2026-01-15T10:00:00.000000Z")
        _insert(db_path, author="Second", message="Msg2", created_at="2026-01-15T11:00:00.000000Z")
        response = client.get(GUESTBOOK_URL)
        assert response.status_code == 200
        html = _html(response)
        assert "First" in html
        assert "Second" in html
        assert "Msg1" in html
        assert "Msg2" in html
        assert html.index("Second") < html.index("First")

    def test_entry_displays_relative_time(self, client, db_path):
        _insert(db_path, created_at="2020-01-01T00:00:00.000000Z")
        response = client.get(GUESTBOOK_URL)
        html = _html(response)
        assert "ago" in html

    def test_empty_state_shows_message(self, client):
        response = client.get(GUESTBOOK_URL)
        assert response.status_code == 200
        html = _html(response)
        assert "No comments yet" in html

    def test_entries_have_data_entry_id(self, client, db_path):
        entry = _insert(db_path)
        response = client.get(GUESTBOOK_URL)
        html = _html(response)
        assert f'data-entry-id="{entry["id"]}"' in html


class TestGuestbookPageForm:
    def test_form_present(self, client):
        response = client.get(GUESTBOOK_URL)
        html = _html(response)
        assert "<form" in html
        assert 'name="name"' in html
        assert 'name="message"' in html
        assert 'type="submit"' in html or "<button" in html

    def test_form_cleared_after_success(self, client):
        response = client.post(
            GUESTBOOK_URL,
            data={"name": "Ada", "message": "Hello"},
            follow_redirects=True,
        )
        html = _html(response)
        assert 'value="Ada"' not in html
        assert ">Hello</textarea>" not in html


class TestGuestbookPageSubmission:
    def test_post_valid_creates_entry_and_redirects(self, client):
        response = client.post(
            GUESTBOOK_URL,
            data={"name": "Ada", "message": "Hello"},
        )
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/guestbook")
        follow = client.get(GUESTBOOK_URL)
        html = _html(follow)
        assert "Ada" in html
        assert "Hello" in html

    def test_post_empty_name_shows_error(self, client, db_path):
        response = client.post(
            GUESTBOOK_URL,
            data={"name": "", "message": "Hello"},
        )
        assert response.status_code == 200
        html = _html(response)
        assert "error" in html.lower() or "required" in html.lower() or "Name" in html
        from guestbook.storage import list_entries
        assert list_entries(db_path) == []

    def test_post_empty_message_shows_error(self, client, db_path):
        response = client.post(
            GUESTBOOK_URL,
            data={"name": "Ada", "message": ""},
        )
        assert response.status_code == 200
        html = _html(response)
        assert "error" in html.lower() or "required" in html.lower() or "Message" in html
        from guestbook.storage import list_entries
        assert list_entries(db_path) == []

    def test_post_whitespace_only_blocked(self, client, db_path):
        response = client.post(
            GUESTBOOK_URL,
            data={"name": "   ", "message": "   "},
        )
        assert response.status_code == 200
        from guestbook.storage import list_entries
        assert list_entries(db_path) == []


class TestGuestbookPageSecurity:
    def test_xss_in_author_escaped(self, client, db_path):
        _insert(db_path, author="<script>alert(1)</script>")
        response = client.get(GUESTBOOK_URL)
        html = _html(response)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_in_message_escaped(self, client, db_path):
        _insert(db_path, message="<script>alert(1)</script>")
        response = client.get(GUESTBOOK_URL)
        html = _html(response)
        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;" in html

    def test_no_delete_functionality(self, client, db_path):
        _insert(db_path)
        response = client.get(GUESTBOOK_URL)
        html = _html(response).lower()
        assert "delete" not in html
