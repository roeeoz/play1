import json
from pathlib import Path

from testbed_utils.reports.audit import record_audit_event


def test_two_events_produce_two_lines(tmp_path):
    log = str(tmp_path / "audit.jsonl")
    record_audit_event(
        log_path=log, ts="2024-01-01T10:00:00Z", actor="alice",
        customer_id="C1", year=2024, outcome="success", path="/reports/C1/2024/annual_claims.pdf",
    )
    record_audit_event(
        log_path=log, ts="2024-01-01T11:00:00Z", actor="bob",
        customer_id="C2", year=2023, outcome="error", error="CustomerNotFound",
    )
    lines = Path(log).read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2


def test_file_not_truncated_on_second_write(tmp_path):
    log = str(tmp_path / "audit.jsonl")
    record_audit_event(
        log_path=log, ts="2024-01-01T10:00:00Z", actor="alice",
        customer_id="C1", year=2024, outcome="success",
    )
    size_after_first = Path(log).stat().st_size
    record_audit_event(
        log_path=log, ts="2024-01-01T11:00:00Z", actor="alice",
        customer_id="C1", year=2024, outcome="success",
    )
    size_after_second = Path(log).stat().st_size
    assert size_after_second > size_after_first


def test_each_line_is_valid_json(tmp_path):
    log = str(tmp_path / "audit.jsonl")
    record_audit_event(
        log_path=log, ts="2024-06-15T08:30:00Z", actor="system",
        customer_id="CU99", year=2024, outcome="success", path="/some/path",
    )
    record_audit_event(
        log_path=log, ts="2024-06-15T08:31:00Z", actor="system",
        customer_id="CU100", year=2023, outcome="error", error="Timeout",
    )
    for line in Path(log).read_text(encoding="utf-8").strip().splitlines():
        obj = json.loads(line)
        assert isinstance(obj, dict)


def test_required_keys_present(tmp_path):
    log = str(tmp_path / "audit.jsonl")
    record_audit_event(
        log_path=log, ts="2024-03-15T12:00:00Z", actor="batch-scheduler",
        customer_id="CU1", year=2024, outcome="success", path="/p", error=None,
    )
    obj = json.loads(Path(log).read_text(encoding="utf-8").strip())
    for key in ("ts", "actor", "customer_id", "year", "outcome", "path", "error"):
        assert key in obj


def test_none_serialised_as_null(tmp_path):
    log = str(tmp_path / "audit.jsonl")
    record_audit_event(
        log_path=log, ts="2024-03-15T12:00:00Z", actor="user1",
        customer_id="CU1", year=2024, outcome="success", path=None, error=None,
    )
    obj = json.loads(Path(log).read_text(encoding="utf-8").strip())
    assert obj["path"] is None
    assert obj["error"] is None


def test_field_values_match_inputs(tmp_path):
    log = str(tmp_path / "audit.jsonl")
    record_audit_event(
        log_path=log,
        ts="2024-12-31T23:59:59Z",
        actor="admin@example.com",
        customer_id="CU-SPECIAL",
        year=2022,
        outcome="error",
        path="/archive/CU-SPECIAL/2022/annual_claims.pdf",
        error="PDF builder failed",
    )
    obj = json.loads(Path(log).read_text(encoding="utf-8").strip())
    assert obj["ts"] == "2024-12-31T23:59:59Z"
    assert obj["actor"] == "admin@example.com"
    assert obj["customer_id"] == "CU-SPECIAL"
    assert obj["year"] == 2022
    assert obj["outcome"] == "error"
    assert obj["path"] == "/archive/CU-SPECIAL/2022/annual_claims.pdf"
    assert obj["error"] == "PDF builder failed"


def test_creates_parent_directories(tmp_path):
    log = str(tmp_path / "nested" / "deep" / "audit.jsonl")
    record_audit_event(
        log_path=log, ts="2024-01-01T00:00:00Z", actor="test",
        customer_id="C1", year=2024, outcome="success",
    )
    assert Path(log).exists()


def test_success_outcome(tmp_path):
    log = str(tmp_path / "audit.jsonl")
    record_audit_event(
        log_path=log, ts="t", actor="a", customer_id="C1", year=2024, outcome="success",
    )
    obj = json.loads(Path(log).read_text(encoding="utf-8").strip())
    assert obj["outcome"] == "success"


def test_error_outcome(tmp_path):
    log = str(tmp_path / "audit.jsonl")
    record_audit_event(
        log_path=log, ts="t", actor="a", customer_id="C1", year=2024,
        outcome="error", error="some error",
    )
    obj = json.loads(Path(log).read_text(encoding="utf-8").strip())
    assert obj["outcome"] == "error"
    assert obj["error"] == "some error"
