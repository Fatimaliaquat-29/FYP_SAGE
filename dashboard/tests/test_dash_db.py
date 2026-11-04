"""The queries module: inserts, filters, bad data."""

import sqlite3
from datetime import datetime, timezone

import pytest

from sage_dashboard import queries


def event(patient_id, key, when, type_="fall", severity="high", confidence=0.9, risk=None):
    return {"patient_id": patient_id, "dedupe_key": key, "occurred_at": when, "type": type_,
            "severity": severity, "confidence": confidence, "risk_score": risk, "source": "test"}


def test_foreign_keys_enforced(conn):
    with pytest.raises(sqlite3.IntegrityError):
        queries.insert_event(conn, event(999, "k", "2026-01-01T00:00:00Z"))


def test_upsert_patient_inserts_then_updates(conn):
    pid, created = queries.upsert_patient(conn, "P1", "Ann", 80, "Room 1", "Nani")
    assert created
    pid2, created2 = queries.upsert_patient(conn, "P1", "Ann B", 81, None)
    assert pid2 == pid and not created2
    row = queries.get_patient(conn, pid)
    assert (row["name"], row["age"], row["room"], row["preferred_name"]) == ("Ann B", 81, None, None)
    assert queries.get_patient_id_by_external(conn, "P1") == pid
    assert queries.get_patient_id_by_external(conn, "nobody") is None


@pytest.mark.parametrize("kwargs", [{"age": -1}, {"age": 131}, {"name": ""}, {"preferred_name": "x" * 51}])
def test_patient_constraints(conn, kwargs):
    args = {"external_id": "P1", "name": "Ann", **kwargs}
    with pytest.raises(sqlite3.IntegrityError):
        queries.upsert_patient(conn, **args)


def test_insert_event_and_duplicate(conn):
    pid, _ = queries.upsert_patient(conn, "P1", "Ann")
    assert queries.insert_event(conn, event(pid, "k1", "2026-01-01T00:00:00Z")) is True
    assert queries.insert_event(conn, event(pid, "k1", "2026-01-02T00:00:00Z")) is False
    assert queries.count_events(conn, pid) == 1


@pytest.mark.parametrize("bad", [
    {"type": "trip"}, {"severity": "critical"}, {"confidence": 1.5},
    {"confidence": -0.1}, {"risk_score": 2.0},
])
def test_event_constraints_reject_bad_values(conn, bad):
    pid, _ = queries.upsert_patient(conn, "P1", "Ann")
    ev = event(pid, "k", "2026-01-01T00:00:00Z")
    ev.update(bad)
    with pytest.raises(sqlite3.IntegrityError):
        queries.insert_event(conn, ev)


@pytest.mark.parametrize("bad", [
    ("ab", "A", "h" * 30, "caregiver"),          # username too short
    ("Upper", "A", "h" * 30, "caregiver"),       # not lower case
    ("good", "A", "short", "caregiver"),         # not a real hash
    ("good", "A", "h" * 30, "owner"),            # unknown role
])
def test_user_constraints(conn, bad):
    with pytest.raises(sqlite3.IntegrityError):
        queries.create_user(conn, *bad)


def test_queries_on_empty_database(conn):
    assert queries.list_patients(conn) == []
    assert queries.get_patient(conn, 1) is None
    assert queries.query_events(conn, 1) == []
    assert queries.count_events(conn, 1) == 0
    assert queries.gait_trend(conn, 1) == []
    assert queries.recent_imports(conn) == []
    assert queries.list_users(conn) == []
    assert queries.patient_summary(conn, 1) == {"last_event": None, "open_alerts": 0, "urgent": 0}
    assert queries.check_event(conn, 1, None) is False
    assert queries.uncheck_event(conn, 1) is False


@pytest.fixture
def filled(conn):
    pid, _ = queries.upsert_patient(conn, "P1", "Ann")
    other, _ = queries.upsert_patient(conn, "P2", "Bob")
    for r in [
        event(pid, "a", "2026-10-01T08:00:00Z", "fall", "high"),
        event(pid, "b", "2026-10-02T08:00:00Z", "gait_risk", "low", risk=0.2),
        event(pid, "c", "2026-10-03T08:00:00Z", "gait_risk", "medium", risk=0.5),
        event(pid, "d", "2026-10-04T08:00:00Z", "gait_risk", "high", risk=0.8),
        event(other, "e", "2026-10-03T09:00:00Z", "fall", "high"),
    ]:
        queries.insert_event(conn, r)
    conn.commit()
    return conn, pid


def test_query_newest_first_and_scoped_to_patient(filled):
    conn, pid = filled
    assert [r["dedupe_key"] for r in queries.query_events(conn, pid)] == ["d", "c", "b", "a"]


def test_query_filters(filled):
    conn, pid = filled
    assert queries.count_events(conn, pid, types=["fall"]) == 1
    assert queries.count_events(conn, pid, severities=["medium", "high"]) == 3
    assert queries.count_events(conn, pid, types=["gait_risk"], severities=["low"]) == 1
    got = queries.query_events(conn, pid, start="2026-10-02T08:00:00Z", end="2026-10-04T08:00:00Z")
    assert [r["dedupe_key"] for r in got] == ["c", "b"]  # start inclusive, end exclusive


def test_filter_values_cannot_inject_sql(filled):
    conn, pid = filled
    assert queries.count_events(conn, pid, types=["fall') OR 1=1 --"]) == 0
    # compared as plain text: sorts before every date, so nothing is earlier than it
    assert queries.count_events(conn, pid, end="' OR '1'='1") == 0
    # never escapes the patient filter (the other patient's event stays out)
    assert queries.count_events(conn, pid, start="' OR '1'='1") == 4


def test_query_limit_offset(filled):
    conn, pid = filled
    assert [r["dedupe_key"] for r in queries.query_events(conn, pid, limit=2, offset=1)] == ["c", "b"]


def test_gait_trend_oldest_first_and_only_gait(filled):
    conn, pid = filled
    assert [r["risk_score"] for r in queries.gait_trend(conn, pid)] == [0.2, 0.5, 0.8]
    assert [r["risk_score"] for r in queries.gait_trend(conn, pid, start="2026-10-03T00:00:00Z")] == [0.5, 0.8]


def test_check_records_who_and_when_and_can_be_undone(filled, user_ids):
    conn, pid = filled
    summary = queries.patient_summary(conn, pid)
    assert summary["last_event"]["dedupe_key"] == "d"
    assert (summary["open_alerts"], summary["urgent"]) == (3, 2)  # low events never need checking
    open_ids = [r["id"] for r in queries.query_events(conn, pid, open_only=True)]
    assert queries.check_event(conn, open_ids[0], user_ids["caregiver"]) is True
    row = queries.get_event(conn, open_ids[0])
    assert row["checked_by_name"] == "Carl" and row["checked_at"]
    assert queries.check_event(conn, open_ids[0], user_ids["admin"]) is False  # first check kept
    assert queries.get_event(conn, open_ids[0])["checked_by_name"] == "Carl"
    assert queries.patient_summary(conn, pid)["open_alerts"] == 2
    assert queries.uncheck_event(conn, open_ids[0]) is True
    row = queries.get_event(conn, open_ids[0])
    assert row["checked_at"] is None and row["checked_by"] is None
    assert queries.patient_summary(conn, pid)["open_alerts"] == 3


def test_deleting_a_user_keeps_their_checks(filled, user_ids):
    conn, pid = filled
    event_id = queries.query_events(conn, pid, open_only=True)[0]["id"]
    queries.check_event(conn, event_id, user_ids["caregiver"])
    queries.delete_user(conn, user_ids["caregiver"])
    row = queries.get_event(conn, event_id)
    assert row["checked_at"] is not None and row["checked_by"] is None


def test_import_log(conn, user_ids):
    import_id = queries.start_import(conn, "file:x.json", user_ids["admin"])
    queries.finish_import(conn, import_id, 3, 1, 2, error=None)
    row = queries.recent_imports(conn)[0]
    assert (row["source"], row["added"], row["duplicates"], row["rejected"], row["imported_by_name"]) == \
        ("file:x.json", 3, 1, 2, "Anna")


def test_login_failure_rows(conn):
    queries.save_login_failure(conn, "someone", 2, "2026-01-01T00:00:00Z", None)
    queries.save_login_failure(conn, "someone", 3, "2026-01-01T00:00:00Z", "2026-01-01T00:05:00Z")
    row = queries.get_login_failure(conn, "someone")
    assert (row["failures"], row["locked_until"]) == (3, "2026-01-01T00:05:00Z")
    queries.clear_login_failures(conn, "someone")
    assert queries.get_login_failure(conn, "someone") is None


def test_utc_helpers():
    dt = datetime(2026, 11, 2, 15, 42, tzinfo=timezone.utc)
    s = queries.to_utc_string(dt)
    assert s == "2026-11-02T15:42:00Z"
    assert queries.parse_utc_string(s) == dt
    with pytest.raises(ValueError):
        queries.to_utc_string(datetime(2026, 11, 2))
