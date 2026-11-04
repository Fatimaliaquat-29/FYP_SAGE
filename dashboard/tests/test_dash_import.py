"""The data-source layer: JSON import validation, duplicates, bad and empty input."""

import json
from datetime import datetime, timedelta, timezone

import pytest

import manage
from conftest import SAMPLE_FILE, ago, fall, gait, iso, load, patient, payload
from sage_dashboard import queries
from sage_dashboard.sources import RecordError, default_severity, validate_event

TECHNICAL_WORDS = ("json", "utf", "iso", "format_version", "risk_score", "confidence", "\"")


def events_in(conn, patient_id=1):
    return list(reversed(queries.query_events(conn, patient_id, limit=1000)))


# --- valid files ----------------------------------------------------------------------

def test_sample_file_imports(conn):
    result = load(conn, SAMPLE_FILE.read_bytes(), "sample_events.json")
    assert result.error is None
    assert (result.added, result.duplicates, result.rejected) == (10, 0, 0)
    assert result.patients_added == 1
    by_key = {r["dedupe_key"]: r for r in events_in(conn)}
    assert by_key["id:P001:Normal_Fall_2:f287"]["severity"] == "high"
    assert by_key["id:P001:walk_2026-10-05"]["severity"] == "low"
    assert by_key["id:P001:walk_2026-10-31"]["severity"] == "medium"
    assert by_key["id:P001:Normal_Fall_2:f287"]["occurred_at"] == "2026-11-01T10:42:00Z"
    assert json.loads(by_key["id:P001:Normal_Fall_1:f412"]["details_json"])["frame"] == 412
    assert queries.recent_imports(conn)[0]["added"] == 10


def test_reimport_adds_nothing(conn):
    load(conn, SAMPLE_FILE.read_bytes())
    result = load(conn, SAMPLE_FILE.read_bytes())
    assert (result.added, result.duplicates, result.rejected) == (0, 10, 0)
    assert result.patients_updated == 1
    assert len(events_in(conn)) == 10


def test_duplicates_inside_one_file(conn):
    when = ago(hours=1)
    no_id = {"patient": "P001", "timestamp": iso(when), "type": "fall", "confidence": 0.7}
    result = load(conn, payload([fall(1, when), fall(1, when), no_id, dict(no_id)]))
    assert (result.added, result.duplicates) == (2, 2)


def test_same_time_different_type_is_not_duplicate(conn):
    when = iso(ago(hours=1))
    a = {"patient": "P001", "timestamp": when, "type": "fall", "confidence": 0.7}
    b = {"patient": "P001", "timestamp": when, "type": "gait_risk", "confidence": 0.7, "risk_score": 0.2}
    assert load(conn, payload([a, b])).added == 2


def test_bom_and_offsets(conn):
    raw = "﻿".encode("utf-8") + payload([{
        "patient": "P001", "timestamp": "2026-10-01T12:00:00+05:00", "type": "fall", "confidence": 0.8}])
    assert load(conn, raw).added == 1
    assert events_in(conn)[0]["occurred_at"] == "2026-10-01T07:00:00Z"


def test_naive_timestamp_is_local_time(conn):
    naive = "2026-10-01T12:00:00"
    expected = datetime.fromisoformat(naive).astimezone().astimezone(timezone.utc)
    load(conn, payload([{"patient": "P001", "timestamp": naive, "type": "fall", "confidence": 0.8}]))
    assert events_in(conn)[0]["occurred_at"] == queries.to_utc_string(expected)


def test_explicit_severity_and_description_kept(conn):
    load(conn, payload([gait(1, ago(hours=1), 0.9, severity="low", description="Walked to the kitchen.")]))
    row = events_in(conn)[0]
    assert (row["severity"], row["description"]) == ("low", "Walked to the kitchen.")


def test_source_defaults_to_file_name(conn):
    load(conn, payload([fall(1, ago(hours=1))]), filename="clip.json")
    assert events_in(conn)[0]["source"] == "file:clip.json"


def test_patients_known_from_earlier_import(conn):
    load(conn, payload([]))
    assert load(conn, payload([fall(1, ago(hours=1))], patients=[])).added == 1


def test_patient_details_updated_on_reimport(conn):
    load(conn, payload([], patients=[patient(name="Amina")]))
    load(conn, payload([], patients=[patient(name="Amina Rahman", room="Room 4", preferred_name="Nani")]))
    row = queries.list_patients(conn)[0]
    assert (row["name"], row["room"], row["preferred_name"]) == ("Amina Rahman", "Room 4", "Nani")


@pytest.mark.parametrize("risk,expected", [(0.0, "low"), (0.39, "low"), (0.4, "medium"),
                                           (0.69, "medium"), (0.7, "high"), (1.0, "high")])
def test_default_gait_severity(risk, expected):
    assert default_severity("gait_risk", risk) == expected


# --- whole-file problems ------------------------------------------------------------

@pytest.mark.parametrize("raw,fragment,kind", [
    (b"", "empty", "unreadable"),
    (b"   \n\t ", "empty", "unreadable"),
    (b"{\"events\": [", "not valid JSON", "unreadable"),
    (b"not json at all", "not valid JSON", "unreadable"),
    (b"\xff\xfe\x00bad", "UTF-8", "unreadable"),
    (b"{\"events\": [{\"confidence\": NaN}]}", "not valid JSON", "unreadable"),
    (b"[]", "one JSON object", "shape"),
    (b"\"text\"", "one JSON object", "shape"),
    (b"{}", "no \"events\" list", "shape"),
    (b"{\"events\": {}}", "no \"events\" list", "shape"),
    (b"{\"events\": [], \"patients\": {}}", "\"patients\" must be a list", "shape"),
    (b"{\"format_version\": 2, \"events\": []}", "Unsupported format_version", "shape"),
])
def test_unusable_files_store_nothing(conn, raw, fragment, kind):
    result = load(conn, raw)
    assert result.error and fragment in result.error
    assert result.error_kind == kind
    assert result.error_plain and not any(w in result.error_plain.lower() for w in TECHNICAL_WORDS)
    assert result.added == 0
    assert queries.list_patients(conn) == []
    assert queries.recent_imports(conn)[0]["error"] == result.error


def test_file_with_no_events(conn):
    result = load(conn, b"{\"events\": []}")
    assert result.error == "The input has no events in it."
    assert result.error_plain == "There was nothing in the file to add."
    assert result.added == 0


# --- record problems ----------------------------------------------------------------

GOOD = {"patient": "P001", "type": "fall", "confidence": 0.9}


def good_event(**changes):
    ev = {**GOOD, "timestamp": iso(ago(hours=1)), **changes}
    return {k: v for k, v in ev.items() if v is not ...}


@pytest.mark.parametrize("record,fragment", [
    (good_event(patient=...), "missing \"patient\""),
    (good_event(patient="  "), "\"patient\" is empty"),
    (good_event(patient=7), "\"patient\" must be text"),
    (good_event(timestamp=...), "missing \"timestamp\""),
    (good_event(timestamp="yesterday"), "not a valid ISO 8601"),
    (good_event(timestamp=12345), "must be ISO 8601 text"),
    (good_event(timestamp=iso(datetime.now(timezone.utc) + timedelta(days=3))), "in the future"),
    (good_event(timestamp="1999-12-31T00:00:00+00:00"), "before the year 2000"),
    (good_event(type=...), "missing \"type\""),
    (good_event(type="trip"), "\"type\" must be one of"),
    (good_event(confidence=...), "missing \"confidence\""),
    (good_event(confidence=1.5), "between 0 and 1"),
    (good_event(confidence="0.9"), "must be a number"),
    (good_event(confidence=True), "must be a number"),
    (good_event(type="gait_risk"), "missing \"risk_score\""),
    (good_event(type="gait_risk", risk_score=-0.2), "between 0 and 1"),
    (good_event(severity="critical"), "\"severity\" must be one of"),
    (good_event(details=[1, 2]), "\"details\" must be an object"),
    (good_event(details={"blob": "x" * 20_000}), "larger than"),
    (good_event(description="x" * 501), "longer than 500"),
    ("just a string", "must be an object"),
    (None, "must be an object"),
])
def test_bad_records_are_reported_and_skipped(conn, record, fragment):
    result = load(conn, payload([record, fall(99, ago(hours=2))]))
    assert result.added == 1, "the valid record in the same file is still stored"
    assert result.rejected == 1
    problem = result.problems[0]
    assert problem.where == "Event 1" and problem.plain_where == "Entry 1"
    assert fragment in problem.technical
    assert not any(w in problem.plain.lower() for w in TECHNICAL_WORDS), problem.plain


def test_unknown_patient_rejected(conn):
    result = load(conn, payload([fall(1, ago(hours=1), pid="P404")]))
    assert result.added == 0
    assert "unknown patient \"P404\"" in result.problems[0].technical
    assert result.problems[0].plain == "It is about a person who has not been added yet."


@pytest.mark.parametrize("record,fragment", [
    ({"name": "No id"}, "missing \"id\""),
    ({"id": "P9"}, "missing \"name\""),
    ({"id": "P9", "name": "A", "age": -3}, "\"age\""),
    ({"id": "P9", "name": "A", "age": True}, "\"age\""),
    ({"id": "P9", "name": "A", "age": 80.5}, "\"age\""),
    ({"id": "P9", "name": "A", "preferred_name": "x" * 51}, "longer than 50"),
    ([], "must be an object"),
])
def test_bad_patients_reported(conn, record, fragment):
    result = load(conn, payload([], patients=[record, patient()]))
    assert result.patients_added == 1
    assert result.problems[0].where == "Patient 1"
    assert fragment in result.problems[0].technical


def test_validate_event_is_pure():
    with pytest.raises(RecordError):
        validate_event({"patient": "P1"})


# --- command line -------------------------------------------------------------------

def test_cli_import(db_path, capsys):
    assert manage.main(["--db", str(db_path), "import", str(SAMPLE_FILE)]) == 0
    assert "10 added" in capsys.readouterr().out
    assert manage.main(["--db", str(db_path), "import", str(SAMPLE_FILE)]) == 0
    assert "10 already present" in capsys.readouterr().out


def test_cli_import_errors(db_path, tmp_path, capsys):
    assert manage.main(["--db", str(db_path), "import", str(tmp_path / "missing.json")]) == 2
    bad = tmp_path / "bad.json"
    bad.write_text("{oops", encoding="utf-8")
    assert manage.main(["--db", str(db_path), "import", str(bad)]) == 1
    assert "not valid JSON" in capsys.readouterr().err
