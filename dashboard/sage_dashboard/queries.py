"""Every SQL statement the dashboard runs lives in this module.

Rules kept here so they are easy to review:
- each statement is one fixed string; values are always passed as
  parameters, never joined into the SQL text;
- optional filters use "(:x IS NULL OR column = :x)" and lists are passed
  as a JSON array read with json_each(), so no SQL is built at run time;
- the table structure comes only from ../schema.sql.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_FILE = Path(__file__).resolve().parent.parent / "schema.sql"
SCHEMA_VERSION = 3

EVENT_TYPES = ("fall", "gait_risk")
SEVERITIES = ("low", "medium", "high")
ROLES = ("caregiver", "admin")
PIPELINE_EVENT_TYPES = ("person_detected", "person_left", "possible_fall", "fall_alert", "gait_risk")
# Severities a caregiver is asked to check on. "low" is information only.
# (Mirrored in the open_only filter inside the SQL below.)
ATTENTION_SEVERITIES = ("medium", "high")

UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class DatabaseNotReady(Exception):
    """The database file is missing or was not set up with schema.sql."""


# --- time helpers --------------------------------------------------------------

def utc_now():
    return datetime.now(timezone.utc).strftime(UTC_FORMAT)


def to_utc_string(dt):
    if dt.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    return dt.astimezone(timezone.utc).strftime(UTC_FORMAT)


def parse_utc_string(value):
    return datetime.strptime(value, UTC_FORMAT).replace(tzinfo=timezone.utc)


# --- connecting and setup --------------------------------------------------------

def create_database(path):
    """Apply schema.sql to `path`, creating the file if needed. Safe to repeat."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")
    conn = sqlite3.connect(path)
    try:
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()


def connect(path):
    """Open an existing, set-up database. Never creates a file."""
    path = Path(path)
    if not path.is_file():
        raise DatabaseNotReady(f"no database file at {path}")
    conn = sqlite3.connect(f"{path.resolve().as_uri()}?mode=rw", uri=True,
                           check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    if schema_version(conn) != SCHEMA_VERSION:
        conn.close()
        raise DatabaseNotReady(f"database at {path} is not set up with schema version {SCHEMA_VERSION}")
    return conn


def schema_version(conn):
    return conn.execute("PRAGMA user_version").fetchone()[0]


def list_tables(conn):
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    return [r[0] for r in rows]


def list_indexes(conn):
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'index' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    return [r[0] for r in rows]


def get_revision(conn):
    return conn.execute("SELECT revision FROM data_version WHERE id = 1").fetchone()[0]


# --- patients ----------------------------------------------------------------------

def upsert_patient(conn, external_id, name, age=None, room=None, preferred_name=None):
    """Add a person, or update their details. Returns (patient_id, created)."""
    now = utc_now()
    existing = get_patient_id_by_external(conn, external_id)
    if existing is not None:
        conn.execute(
            "UPDATE patients SET name = :name, preferred_name = :preferred_name, age = :age,"
            " room = :room, updated_at = :now WHERE id = :id",
            {"name": name, "preferred_name": preferred_name, "age": age, "room": room,
             "now": now, "id": existing})
        return existing, False
    cur = conn.execute(
        "INSERT INTO patients (external_id, name, preferred_name, age, room, created_at, updated_at)"
        " VALUES (:external_id, :name, :preferred_name, :age, :room, :now, :now)",
        {"external_id": external_id, "name": name, "preferred_name": preferred_name,
         "age": age, "room": room, "now": now})
    return cur.lastrowid, True


def get_patient(conn, patient_id):
    return conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()


def get_patient_id_by_external(conn, external_id):
    row = conn.execute("SELECT id FROM patients WHERE external_id = ?", (external_id,)).fetchone()
    return row["id"] if row else None


def list_patients(conn):
    return conn.execute("SELECT * FROM patients ORDER BY name COLLATE NOCASE, id").fetchall()


def patient_summary(conn, patient_id):
    """Last event, number of events waiting to be checked, and whether any is urgent."""
    last = conn.execute(
        "SELECT * FROM events WHERE patient_id = ? ORDER BY occurred_at DESC, id DESC LIMIT 1",
        (patient_id,)).fetchone()
    counts = conn.execute(
        "SELECT COUNT(*) AS open_alerts,"
        " COALESCE(SUM(severity = 'high'), 0) AS urgent"
        " FROM events WHERE patient_id = ? AND checked_at IS NULL"
        " AND severity IN ('medium', 'high')",
        (patient_id,)).fetchone()
    return {"last_event": last, "open_alerts": counts["open_alerts"], "urgent": counts["urgent"]}


# --- events --------------------------------------------------------------------------

def insert_event(conn, event):
    """Store one validated event. Returns True if added, False if it was a duplicate.

    Only a repeated dedupe_key is skipped; any other constraint failure raises.
    """
    values = {"import_id": None, "description": None, "risk_score": None,
              "details_json": "{}", "created_at": utc_now(), **event}
    cur = conn.execute(
        "INSERT INTO events (patient_id, dedupe_key, occurred_at, type, severity, confidence,"
        " risk_score, source, description, details_json, import_id, created_at)"
        " VALUES (:patient_id, :dedupe_key, :occurred_at, :type, :severity, :confidence,"
        " :risk_score, :source, :description, :details_json, :import_id, :created_at)"
        " ON CONFLICT (dedupe_key) DO NOTHING",
        values)
    return cur.rowcount == 1


def _filter_params(patient_id, types=None, severities=None, start=None, end=None,
                   open_only=False):
    """Parameters for the shared event filter. start inclusive, end exclusive (UTC)."""
    return {"patient_id": patient_id,
            "types": json.dumps(list(types)) if types else None,
            "severities": json.dumps(list(severities)) if severities else None,
            "start": start, "end": end, "open_only": 1 if open_only else 0}


def query_events(conn, patient_id, limit=50, offset=0, **filters):
    params = _filter_params(patient_id, **filters)
    params.update(limit=limit, offset=offset)
    return conn.execute(
        "SELECT e.*, u.display_name AS checked_by_name"
        " FROM events e LEFT JOIN users u ON u.id = e.checked_by"
        " WHERE e.patient_id = :patient_id"
        " AND (:types IS NULL OR e.type IN (SELECT value FROM json_each(:types)))"
        " AND (:severities IS NULL OR e.severity IN (SELECT value FROM json_each(:severities)))"
        " AND (:start IS NULL OR e.occurred_at >= :start)"
        " AND (:end IS NULL OR e.occurred_at < :end)"
        " AND (:open_only = 0 OR (e.checked_at IS NULL AND e.severity IN ('medium', 'high')))"
        " ORDER BY e.occurred_at DESC, e.id DESC LIMIT :limit OFFSET :offset",
        params).fetchall()


def count_events(conn, patient_id, **filters):
    return conn.execute(
        "SELECT COUNT(*) FROM events e"
        " WHERE e.patient_id = :patient_id"
        " AND (:types IS NULL OR e.type IN (SELECT value FROM json_each(:types)))"
        " AND (:severities IS NULL OR e.severity IN (SELECT value FROM json_each(:severities)))"
        " AND (:start IS NULL OR e.occurred_at >= :start)"
        " AND (:end IS NULL OR e.occurred_at < :end)"
        " AND (:open_only = 0 OR (e.checked_at IS NULL AND e.severity IN ('medium', 'high')))",
        _filter_params(patient_id, **filters)).fetchone()[0]


def get_event(conn, event_id):
    return conn.execute(
        "SELECT e.*, u.display_name AS checked_by_name"
        " FROM events e LEFT JOIN users u ON u.id = e.checked_by WHERE e.id = ?",
        (event_id,)).fetchone()


def check_event(conn, event_id, user_id):
    """Mark as checked by this user. Keeps the first check if already checked."""
    cur = conn.execute(
        "UPDATE events SET checked_at = :now, checked_by = :user_id"
        " WHERE id = :id AND checked_at IS NULL",
        {"now": utc_now(), "user_id": user_id, "id": event_id})
    conn.commit()
    return cur.rowcount == 1


def uncheck_event(conn, event_id):
    """Undo "I've checked"."""
    cur = conn.execute(
        "UPDATE events SET checked_at = NULL, checked_by = NULL"
        " WHERE id = ? AND checked_at IS NOT NULL", (event_id,))
    conn.commit()
    return cur.rowcount == 1


def gait_trend(conn, patient_id, start=None):
    """Walking risk scores in time order, oldest first."""
    return conn.execute(
        "SELECT occurred_at, risk_score, severity FROM events"
        " WHERE patient_id = :patient_id AND type = 'gait_risk' AND risk_score IS NOT NULL"
        " AND (:start IS NULL OR occurred_at >= :start)"
        " ORDER BY occurred_at, id",
        {"patient_id": patient_id, "start": start}).fetchall()


# --- imports -------------------------------------------------------------------------

def start_import(conn, source, user_id=None):
    cur = conn.execute(
        "INSERT INTO imports (source, imported_at, imported_by) VALUES (?, ?, ?)",
        (source, utc_now(), user_id))
    return cur.lastrowid


def finish_import(conn, import_id, added, duplicates, rejected, error=None):
    conn.execute(
        "UPDATE imports SET added = ?, duplicates = ?, rejected = ?, error = ? WHERE id = ?",
        (added, duplicates, rejected, error, import_id))


def recent_imports(conn, limit=5):
    return conn.execute(
        "SELECT i.*, u.display_name AS imported_by_name"
        " FROM imports i LEFT JOIN users u ON u.id = i.imported_by"
        " ORDER BY i.imported_at DESC, i.id DESC LIMIT ?", (limit,)).fetchall()


# --- users ---------------------------------------------------------------------------

def create_user(conn, username, display_name, password_hash, role):
    cur = conn.execute(
        "INSERT INTO users (username, display_name, password_hash, role, created_at)"
        " VALUES (?, ?, ?, ?, ?)",
        (username, display_name, password_hash, role, utc_now()))
    conn.commit()
    return cur.lastrowid


def get_user(conn, user_id):
    return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_user_by_username(conn, username):
    return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def list_users(conn):
    return conn.execute("SELECT * FROM users ORDER BY display_name COLLATE NOCASE, id").fetchall()


def count_users(conn):
    return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]


def count_admins(conn):
    return conn.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'").fetchone()[0]


def set_password_hash(conn, user_id, password_hash):
    cur = conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
    conn.commit()
    return cur.rowcount == 1


def delete_user(conn, user_id):
    cur = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    return cur.rowcount == 1


def record_login(conn, user_id):
    conn.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (utc_now(), user_id))
    conn.commit()


# --- failed sign-ins -------------------------------------------------------------------

def get_login_failure(conn, username):
    return conn.execute("SELECT * FROM login_failures WHERE username = ?", (username,)).fetchone()


def save_login_failure(conn, username, failures, first_failed_at, locked_until):
    conn.execute(
        "INSERT INTO login_failures (username, failures, first_failed_at, locked_until)"
        " VALUES (:username, :failures, :first, :locked)"
        " ON CONFLICT (username) DO UPDATE SET failures = :failures,"
        " first_failed_at = :first, locked_until = :locked",
        {"username": username, "failures": failures, "first": first_failed_at,
         "locked": locked_until})
    conn.commit()


def clear_login_failures(conn, username):
    conn.execute("DELETE FROM login_failures WHERE username = ?", (username,))
    conn.commit()


# --- live demo pipeline log ----------------------------------------------------------

def insert_pipeline_event(conn, event):
    """Store one event noticed by the live video processing. Returns its id."""
    values = {"confidence": None, "video_time": None, "frame": None, "loop_number": 1,
              "details_json": "{}", "occurred_at": utc_now(), **event}
    cur = conn.execute(
        "INSERT INTO pipeline_log (occurred_at, type, confidence, source, video_time, frame,"
        " loop_number, details_json)"
        " VALUES (:occurred_at, :type, :confidence, :source, :video_time, :frame,"
        " :loop_number, :details_json)",
        values)
    conn.commit()
    return cur.lastrowid


def pipeline_events_after(conn, after_id=0, limit=100):
    """Newest first; only events with an id above `after_id`."""
    return conn.execute(
        "SELECT * FROM pipeline_log WHERE id > ? ORDER BY id DESC LIMIT ?",
        (after_id, limit)).fetchall()


def pipeline_event_counts(conn):
    """{type: count} for every type that has occurred."""
    rows = conn.execute("SELECT type, COUNT(*) AS n FROM pipeline_log GROUP BY type").fetchall()
    return {r["type"]: r["n"] for r in rows}


def latest_pipeline_event(conn):
    return conn.execute("SELECT * FROM pipeline_log ORDER BY id DESC LIMIT 1").fetchone()
