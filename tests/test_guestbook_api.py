import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pytest

from guestbook.app import DB_PATH_ENV, create_app
from guestbook.validation import AUTHOR_MAX, MESSAGE_MAX

ENTRIES_URL = "/api/guestbook/entries"
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
ENTRY_KEYS = {"id", "author", "message", "created_at"}


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "guestbook.sqlite3")


@pytest.fixture
def app(db_path):
    return create_app(db_path=db_path)


@pytest.fixture
def client(app):
    return app.test_client()


def post(client, body):
    """POST *body* as JSON, or as a raw string when it is already text."""
    if isinstance(body, str):
        return client.post(ENTRIES_URL, data=body, content_type="application/json")
    return client.post(ENTRIES_URL, json=body)


def sort_key_desc(entries):
    """Return *entries* in the order the API promises: newest first."""
    return sorted(entries, key=lambda entry: (entry["created_at"], entry["id"]), reverse=True)


def create(client, author="Ada", message="Hello"):
    response = post(client, {"author": author, "message": message})
    assert response.status_code == 201
    return response.get_json()


class TestCreateEntry:
    def test_returns_created_entry(self, client):
        response = post(client, {"author": "Ada", "message": "Hello there"})
        assert response.status_code == 201
        entry = response.get_json()
        assert set(entry) == ENTRY_KEYS
        assert entry["author"] == "Ada"
        assert entry["message"] == "Hello there"
        assert isinstance(entry["id"], int)

    def test_created_at_is_server_set_utc(self, client):
        entry = create(client)
        assert entry["created_at"].endswith("Z")
        datetime.strptime(entry["created_at"], TIMESTAMP_FORMAT)

    def test_client_supplied_id_and_created_at_are_ignored(self, client):
        response = post(
            client,
            {
                "author": "Ada",
                "message": "Hello",
                "id": 999,
                "created_at": "1999-01-01T00:00:00.000000Z",
            },
        )
        entry = response.get_json()
        assert entry["id"] != 999
        assert entry["created_at"] != "1999-01-01T00:00:00.000000Z"

    def test_values_are_trimmed(self, client):
        entry = create(client, author="  Ada  ", message="  Hello  ")
        assert entry["author"] == "Ada"
        assert entry["message"] == "Hello"
        listed = client.get(ENTRIES_URL).get_json()
        assert listed[0]["author"] == "Ada"
        assert listed[0]["message"] == "Hello"

    @pytest.mark.parametrize(
        "author, message",
        [
            ("a", "b"),
            ("x" * AUTHOR_MAX, "y" * MESSAGE_MAX),
            ("א" * AUTHOR_MAX, "ש" * MESSAGE_MAX),
            ("🙂" * AUTHOR_MAX, "🙂" * MESSAGE_MAX),
        ],
    )
    def test_length_boundaries_accepted(self, client, author, message):
        entry = create(client, author=author, message=message)
        assert entry["author"] == author
        assert entry["message"] == message

    def test_identical_posts_create_distinct_entries(self, client):
        first = create(client)
        second = create(client)
        assert first["id"] != second["id"]
        assert len(client.get(ENTRIES_URL).get_json()) == 2


class TestCreateValidation:
    @pytest.mark.parametrize("field", ["author", "message"])
    @pytest.mark.parametrize(
        "value, present",
        [
            (None, False),
            (None, True),
            (7, True),
            ("", True),
            ("   ", True),
        ],
    )
    def test_rejects_bad_field(self, client, field, value, present):
        body = {"author": "Ada", "message": "Hello"}
        if present:
            body[field] = value
        else:
            del body[field]
        response = post(client, body)
        assert response.status_code == 400
        error = response.get_json()["error"]
        assert error["code"] == "validation_error"
        assert set(error["fields"]) == {field}
        assert client.get(ENTRIES_URL).get_json() == []

    @pytest.mark.parametrize(
        "field, value",
        [("author", "x" * (AUTHOR_MAX + 1)), ("message", "y" * (MESSAGE_MAX + 1))],
    )
    def test_rejects_too_long_field(self, client, field, value):
        body = {"author": "Ada", "message": "Hello"}
        body[field] = value
        response = post(client, body)
        assert response.status_code == 400
        assert set(response.get_json()["error"]["fields"]) == {field}
        assert client.get(ENTRIES_URL).get_json() == []

    def test_whitespace_padded_overlong_value_is_rejected_on_trimmed_length(self, client):
        response = post(client, {"author": " " + "x" * (AUTHOR_MAX + 1) + " ", "message": "Hi"})
        assert response.status_code == 400
        assert set(response.get_json()["error"]["fields"]) == {"author"}

    def test_both_fields_can_fail_together(self, client):
        response = post(client, {"author": "   ", "message": ""})
        assert response.status_code == 400
        fields = response.get_json()["error"]["fields"]
        assert set(fields) == {"author", "message"}
        assert all(isinstance(message, str) and message for message in fields.values())

    def test_rejection_leaves_existing_entries_untouched(self, client):
        existing = create(client)
        assert post(client, {"author": "", "message": ""}).status_code == 400
        assert client.get(ENTRIES_URL).get_json() == [existing]


class TestInvalidJson:
    @pytest.mark.parametrize("body", ["not json", "[]", "null", "", '"text"', "12"])
    def test_rejects_non_object_body(self, client, body):
        response = post(client, body)
        assert response.status_code == 400
        error = response.get_json()["error"]
        assert error["code"] == "invalid_json"
        assert "fields" not in error
        assert client.get(ENTRIES_URL).get_json() == []


class TestListEntries:
    def test_empty_database_returns_empty_array(self, client):
        response = client.get(ENTRIES_URL)
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_every_entry_with_all_fields(self, client):
        created = [create(client, author=f"A{index}", message=f"M{index}") for index in range(3)]
        listed = client.get(ENTRIES_URL).get_json()
        assert len(listed) == 3
        assert all(set(entry) == ENTRY_KEYS for entry in listed)
        assert sorted(listed, key=lambda entry: entry["id"]) == created

    def test_newest_first(self, client):
        create(client, author="first")
        create(client, author="second")
        listed = client.get(ENTRIES_URL).get_json()
        assert [entry["author"] for entry in listed] == ["second", "first"]

    def test_order_is_stable_across_calls(self, client):
        for index in range(5):
            create(client, message=f"m{index}")
        first = client.get(ENTRIES_URL).get_json()
        second = client.get(ENTRIES_URL).get_json()
        assert first == second
        ids = [entry["id"] for entry in first]
        assert ids == sorted(ids, reverse=True)


class TestNoPagination:
    def test_hundred_entries_all_returned_in_order(self, client):
        for index in range(100):
            create(client, message=f"entry {index}")
        listed = client.get(ENTRIES_URL).get_json()
        assert len(listed) == 100
        ids = [entry["id"] for entry in listed]
        assert ids == sorted(ids, reverse=True)
        assert [entry["message"] for entry in listed][0] == "entry 99"
        assert client.get(ENTRIES_URL).get_json() == listed


class TestAppSetup:
    def test_creates_database_file_and_missing_parent(self, tmp_path):
        path = tmp_path / "nested" / "dir" / "guestbook.sqlite3"
        create_app(db_path=str(path))
        assert path.exists()

    def test_environment_variable_is_used_when_no_argument(self, tmp_path, monkeypatch):
        path = tmp_path / "from-env.sqlite3"
        monkeypatch.setenv(DB_PATH_ENV, str(path))
        app = create_app()
        assert app.config["GUESTBOOK_DB_PATH"] == str(path)
        assert path.exists()

    def test_argument_overrides_environment_variable(self, tmp_path, monkeypatch):
        monkeypatch.setenv(DB_PATH_ENV, str(tmp_path / "env.sqlite3"))
        explicit = str(tmp_path / "explicit.sqlite3")
        assert create_app(db_path=explicit).config["GUESTBOOK_DB_PATH"] == explicit

    def test_concurrent_creates_are_safe(self, app):
        def send(index):
            response = app.test_client().post(
                ENTRIES_URL, json={"author": f"A{index}", "message": f"M{index}"}
            )
            assert response.status_code == 201
            return response.get_json()["id"]

        with ThreadPoolExecutor(max_workers=8) as pool:
            ids = list(pool.map(send, range(20)))

        assert len(set(ids)) == 20
        listed = app.test_client().get(ENTRIES_URL).get_json()
        assert len(listed) == 20
        assert {entry["id"] for entry in listed} == set(ids)
        # Concurrent requests may stamp their timestamp in one order and insert
        # in another, so only the declared (created_at, id) order is guaranteed.
        assert listed == sort_key_desc(listed)
        assert app.test_client().get(ENTRIES_URL).get_json() == listed

    def test_response_is_json(self, client):
        response = client.get(ENTRIES_URL)
        assert response.mimetype == "application/json"
        assert json.loads(response.get_data(as_text=True)) == []
