"""The single entry point for getting data into the dashboard.

Everything the dashboard shows comes from the database, and everything in
the database arrives through `ingest()`. A data source only has to produce
plain record dicts (see README.md, "Import format"); validation, severity
rules and duplicate handling live here, once.

Sources today:
- JsonFileSource: an uploaded results file from analysed videos.
- PipelineSource: one event (or a batch) sent live to POST /api/events,
  by the demo replay now and by the SAGE pipeline later.

Every rejection carries two messages: a technical one (for the API, the
command line and the README) and a plain one shown on screen.
"""

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from . import queries

FORMAT_VERSION = 1

MAX_TEXT = {"patient": 64, "event_id": 200, "source": 200, "description": 500,
            "name": 100, "room": 100, "preferred_name": 50, "id": 64}
MAX_DETAILS_BYTES = 10_000
# Timestamps further ahead than this are treated as a clock or data error.
FUTURE_TOLERANCE = timedelta(days=1)

# Gait risk score (0-1, from GaitRiskAssessor.assess_risk) to severity,
# used only when a record does not state its own severity.
GAIT_MEDIUM_FROM = 0.4
GAIT_HIGH_FROM = 0.7

# How each field is described to a caregiver.
PLAIN_FIELD = {
    "patient": "which person it is about",
    "timestamp": "the date and time",
    "type": "what kind of event it was",
    "confidence": "how sure the camera was",
    "risk_score": "the walking result",
    "severity": "how important it is",
    "details": "the extra notes",
    "description": "the description",
    "event_id": "the reference number",
    "source": "where it came from",
    "id": "the person's reference",
    "name": "the person's name",
    "preferred_name": "the name they like to be called",
    "age": "the person's age",
    "room": "the room",
}


class SourceError(Exception):
    """The whole input is unusable (empty, unreadable, wrong shape)."""

    def __init__(self, technical, plain, kind="shape"):
        super().__init__(technical)
        self.technical = technical
        self.plain = plain
        self.kind = kind  # "unreadable" (not text/JSON at all) or "shape" (wrong layout)


class RecordError(ValueError):
    """One record is unusable."""

    def __init__(self, technical, plain=None):
        super().__init__(technical)
        self.technical = technical
        self.plain = plain or "Something in it is not filled in correctly."


def _missing(key):
    return RecordError(f"missing \"{key}\"", f"{PLAIN_FIELD[key].capitalize()} is missing.")


def _invalid(key, technical):
    return RecordError(technical, f"{PLAIN_FIELD[key].capitalize()} is not filled in correctly.")


@dataclass
class Problem:
    kind: str          # "Event" or "Patient"
    index: int         # position in the list, from 1
    technical: str
    plain: str

    @property
    def where(self):
        return f"{self.kind} {self.index}"

    @property
    def plain_where(self):
        return f"Entry {self.index}" if self.kind == "Event" else f"Person {self.index}"


@dataclass
class Batch:
    patients: list
    events: list


@dataclass
class ImportResult:
    source: str
    added: int = 0
    duplicates: int = 0
    patients_added: int = 0
    patients_updated: int = 0
    problems: list = field(default_factory=list)  # Problem
    error: str = None         # technical reason the whole input was refused
    error_plain: str = None   # the same, for the screen
    error_kind: str = None    # "unreadable", "shape" or "empty"

    @property
    def rejected(self):
        return len(self.problems)


class DataSource:
    """Something that can hand over a batch of patient and event records."""

    name = "unknown"
    log_to_history = True  # write a row in the imports table

    def read(self):
        """Return a Batch, or raise SourceError if the input is unusable."""
        raise NotImplementedError


def _parse_json(raw):
    if not raw or not raw.strip():
        raise SourceError("The input is empty.", "The file is empty.", "unreadable")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise SourceError("The input is not UTF-8 text.",
                          "This file can't be read. It may be the wrong kind of file.",
                          "unreadable") from None
    try:
        return json.loads(text, parse_constant=_reject_constant)
    except (json.JSONDecodeError, ValueError) as exc:
        raise SourceError(f"The input is not valid JSON ({_json_error(exc)}).",
                          "This file can't be read. It may be damaged or the wrong kind of file.",
                          "unreadable") from None


def _batch_from_object(data):
    if not isinstance(data, dict):
        raise SourceError("Expected one JSON object with an \"events\" list.",
                          "This file is not laid out the way we expect.")
    version = data.get("format_version", FORMAT_VERSION)
    if version != FORMAT_VERSION:
        raise SourceError(f"Unsupported format_version {version!r}; expected {FORMAT_VERSION}.",
                          "This file comes from a different version of the software.")
    events = data.get("events")
    if not isinstance(events, list):
        raise SourceError("The input has no \"events\" list.",
                          "This file does not contain any events.")
    patients = data.get("patients", [])
    if not isinstance(patients, list):
        raise SourceError("\"patients\" must be a list.",
                          "The list of people in this file is not laid out the way we expect.")
    return Batch(patients=patients, events=events)


class JsonFileSource(DataSource):
    """Results of analysed videos, uploaded as one JSON file."""

    def __init__(self, raw_bytes, filename="upload.json"):
        self.raw = raw_bytes
        self.name = f"file:{filename}"

    def read(self):
        return _batch_from_object(_parse_json(self.raw))


class PipelineSource(DataSource):
    """Live input: one event object, or the full import format for a batch."""

    name = "live"
    log_to_history = False

    def __init__(self, raw_bytes):
        self.raw = raw_bytes

    def read(self):
        data = _parse_json(self.raw)
        if isinstance(data, dict) and ("events" in data or "patients" in data):
            if "events" not in data:
                data = {**data, "events": []}
            return _batch_from_object(data)
        if isinstance(data, dict):
            return Batch(patients=[], events=[data])
        raise SourceError("Expected a JSON object: one event, or {\"events\": [...]}.",
                          "This is not laid out the way we expect.")


def _reject_constant(name):
    raise ValueError(f"{name} is not allowed")


def _json_error(exc):
    if isinstance(exc, json.JSONDecodeError):
        return f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
    return str(exc)


# --- validation ---------------------------------------------------------------------

def _text(record, key, required=False):
    value = record.get(key)
    if value is None:
        if required:
            raise _missing(key)
        return None
    if not isinstance(value, str):
        raise _invalid(key, f"\"{key}\" must be text")
    value = value.strip()
    if not value:
        if required:
            raise RecordError(f"\"{key}\" is empty", f"{PLAIN_FIELD[key].capitalize()} is empty.")
        return None
    if len(value) > MAX_TEXT[key]:
        raise _invalid(key, f"\"{key}\" is longer than {MAX_TEXT[key]} characters")
    return value


def _fraction(record, key, required=False):
    value = record.get(key)
    if value is None:
        if required:
            raise _missing(key)
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _invalid(key, f"\"{key}\" must be a number between 0 and 1")
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise _invalid(key, f"\"{key}\" must be between 0 and 1")
    return value


def parse_timestamp(value, now=None):
    """ISO 8601 text to an aware UTC datetime. Naive times are this device's local time."""
    if not isinstance(value, str) or not value.strip():
        raise _invalid("timestamp", "\"timestamp\" must be ISO 8601 text, e.g. 2026-11-02T15:42:00+05:00")
    try:
        dt = datetime.fromisoformat(value.strip())
    except ValueError:
        raise _invalid("timestamp", f"\"timestamp\" {value!r} is not a valid ISO 8601 date and time") from None
    if dt.tzinfo is None:
        dt = dt.astimezone()
    dt = dt.astimezone(timezone.utc)
    now = now or datetime.now(timezone.utc)
    if dt > now + FUTURE_TOLERANCE:
        raise RecordError("\"timestamp\" is in the future", "The date and time is in the future.")
    if dt.year < 2000:
        raise RecordError("\"timestamp\" is before the year 2000", "The date is too far in the past.")
    return dt


def validate_patient(record):
    if not isinstance(record, dict):
        raise RecordError("must be an object", "This entry is not laid out the way we expect.")
    external_id = _text(record, "id", required=True)
    name = _text(record, "name", required=True)
    age = record.get("age")
    if age is not None:
        if isinstance(age, bool) or not isinstance(age, int) or not 0 <= age <= 130:
            raise _invalid("age", "\"age\" must be a whole number between 0 and 130")
    return {"external_id": external_id, "name": name, "age": age,
            "room": _text(record, "room"), "preferred_name": _text(record, "preferred_name")}


def default_severity(event_type, risk_score):
    if event_type == "fall":
        return "high"
    if risk_score >= GAIT_HIGH_FROM:
        return "high"
    if risk_score >= GAIT_MEDIUM_FROM:
        return "medium"
    return "low"


def validate_event(record, now=None):
    """Check one event record. Returns a normalised dict (with "patient", not patient_id)."""
    if not isinstance(record, dict):
        raise RecordError("must be an object", "This entry is not laid out the way we expect.")
    patient = _text(record, "patient", required=True)
    if record.get("timestamp") is None:
        raise _missing("timestamp")
    occurred = parse_timestamp(record["timestamp"], now=now)
    event_type = record.get("type")
    if event_type is None:
        raise _missing("type")
    if event_type not in queries.EVENT_TYPES:
        raise _invalid("type", f"\"type\" must be one of: {', '.join(queries.EVENT_TYPES)}")
    confidence = _fraction(record, "confidence", required=True)
    risk_score = _fraction(record, "risk_score", required=(event_type == "gait_risk"))
    severity = record.get("severity")
    if severity is None:
        severity = default_severity(event_type, risk_score)
    elif severity not in queries.SEVERITIES:
        raise _invalid("severity", f"\"severity\" must be one of: {', '.join(queries.SEVERITIES)}")
    details = record.get("details", {})
    if details is None:
        details = {}
    if not isinstance(details, dict):
        raise _invalid("details", "\"details\" must be an object")
    details_json = json.dumps(details, ensure_ascii=False, sort_keys=True)
    if len(details_json.encode("utf-8")) > MAX_DETAILS_BYTES:
        raise _invalid("details", f"\"details\" is larger than {MAX_DETAILS_BYTES} bytes")
    event_id = _text(record, "event_id")
    occurred_at = queries.to_utc_string(occurred)
    return {
        "patient": patient,
        "dedupe_key": dedupe_key(patient, event_id, occurred_at, event_type),
        "occurred_at": occurred_at,
        "type": event_type,
        "severity": severity,
        "confidence": confidence,
        "risk_score": risk_score,
        "source": _text(record, "source"),
        "description": _text(record, "description"),
        "details_json": details_json,
    }


def dedupe_key(patient, event_id, occurred_at, event_type):
    """Stable identity of an event, so sending it again adds nothing new."""
    if event_id:
        return f"id:{patient}:{event_id}"
    digest = hashlib.sha256(f"{patient}|{occurred_at}|{event_type}".encode("utf-8"))
    return f"h:{digest.hexdigest()}"


# --- ingest -------------------------------------------------------------------------

def ingest(conn, source, user_id=None, now=None):
    """Read a source and store what is valid. Bad records are reported, not fatal.

    Runs in one transaction: either the valid records are all stored or,
    if something unexpected fails, nothing is.
    """
    result = ImportResult(source=source.name)
    try:
        batch = source.read()
    except SourceError as exc:
        result.error, result.error_plain, result.error_kind = exc.technical, exc.plain, exc.kind
        if source.log_to_history:
            import_id = queries.start_import(conn, source.name, user_id)
            queries.finish_import(conn, import_id, 0, 0, 0, error=exc.technical)
            conn.commit()
        return result

    try:
        import_id = queries.start_import(conn, source.name, user_id) if source.log_to_history else None
        for i, record in enumerate(batch.patients, start=1):
            try:
                p = validate_patient(record)
            except RecordError as exc:
                result.problems.append(Problem("Patient", i, exc.technical, exc.plain))
                continue
            _, created = queries.upsert_patient(conn, **p)
            if created:
                result.patients_added += 1
            else:
                result.patients_updated += 1

        for i, record in enumerate(batch.events, start=1):
            try:
                ev = validate_event(record, now=now)
            except RecordError as exc:
                result.problems.append(Problem("Event", i, exc.technical, exc.plain))
                continue
            external = ev.pop("patient")
            patient_id = queries.get_patient_id_by_external(conn, external)
            if patient_id is None:
                result.problems.append(Problem(
                    "Event", i,
                    f"unknown patient \"{external}\"; add them to the \"patients\" list",
                    "It is about a person who has not been added yet."))
                continue
            ev.update(patient_id=patient_id, import_id=import_id,
                      source=ev["source"] or source.name)
            if queries.insert_event(conn, ev):
                result.added += 1
            else:
                result.duplicates += 1

        if not batch.patients and not batch.events:
            result.error = "The input has no events in it."
            result.error_plain = "There was nothing in the file to add."
            result.error_kind = "empty"
        if import_id is not None:
            queries.finish_import(conn, import_id, result.added, result.duplicates,
                                  result.rejected, error=result.error)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return result
