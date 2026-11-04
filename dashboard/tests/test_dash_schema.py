"""schema.sql is the single source of truth, applies cleanly and is idempotent;
all SQL lives in queries.py and is parameterised."""

import ast
import re
import sqlite3

import pytest

from conftest import DASHBOARD_DIR, fall, load, payload, ago
from sage_dashboard import queries

EXPECTED_TABLES = {"patients", "users", "login_failures", "imports", "events", "data_version", "pipeline_log"}


def test_schema_applies_to_empty_database(tmp_path):
    path = tmp_path / "fresh" / "new.sqlite3"
    queries.create_database(path)
    conn = queries.connect(path)
    assert set(queries.list_tables(conn)) == EXPECTED_TABLES
    assert queries.schema_version(conn) == queries.SCHEMA_VERSION
    assert queries.get_revision(conn) == 0
    indexes = set(queries.list_indexes(conn))
    assert {"idx_events_patient_time", "idx_events_patient_type_time",
            "idx_events_patient_sev_time", "idx_events_patient_checked",
            "idx_pipeline_log_time", "idx_pipeline_log_type"} <= indexes
    conn.close()


def test_schema_is_idempotent_and_keeps_data(db_path, user_ids):
    conn = queries.connect(db_path)
    load(conn, payload([fall(1, ago(hours=1))]))
    rev = queries.get_revision(conn)
    conn.close()
    queries.create_database(db_path)
    queries.create_database(db_path)
    conn = queries.connect(db_path)
    assert queries.count_events(conn, 1) == 1
    assert len(queries.list_users(conn)) == 2
    assert queries.get_revision(conn) == rev
    assert set(queries.list_tables(conn)) == EXPECTED_TABLES
    conn.close()


def test_connect_never_creates_a_file(tmp_path):
    missing = tmp_path / "missing.sqlite3"
    with pytest.raises(queries.DatabaseNotReady):
        queries.connect(missing)
    assert not missing.exists()


def test_connect_refuses_database_without_schema(tmp_path):
    empty = tmp_path / "empty.sqlite3"
    sqlite3.connect(empty).close()
    with pytest.raises(queries.DatabaseNotReady):
        queries.connect(empty)


def test_schema_file_has_comments_and_constraints():
    text = (DASHBOARD_DIR / "schema.sql").read_text(encoding="utf-8")
    assert text.count("CREATE TABLE IF NOT EXISTS") == len(EXPECTED_TABLES)
    assert "CREATE TABLE " not in text.replace("CREATE TABLE IF NOT EXISTS", "")
    for word in ("PRIMARY KEY", "REFERENCES", "CHECK", "CREATE INDEX IF NOT EXISTS", "--"):
        assert word in text


def test_revision_rises_when_events_change(conn, user_ids):
    start = queries.get_revision(conn)
    load(conn, payload([fall(1, ago(hours=1))]))
    after_insert = queries.get_revision(conn)
    assert after_insert > start
    queries.check_event(conn, 1, user_ids["admin"])
    assert queries.get_revision(conn) > after_insert


# --- SQL only in queries.py ----------------------------------------------------------

SQL_PATTERN = re.compile(
    r"\b(SELECT\s+.+\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|CREATE\s+(TABLE|INDEX|TRIGGER)"
    r"|DROP\s+TABLE|ALTER\s+TABLE|PRAGMA\s+\w+)\b", re.IGNORECASE)


def app_code_files():
    files = [DASHBOARD_DIR / "manage.py", DASHBOARD_DIR / "demo_replay.py"]
    files += sorted((DASHBOARD_DIR / "sage_dashboard").glob("*.py"))
    files += sorted((DASHBOARD_DIR / "sage_dashboard" / "templates").glob("*.html"))
    files += sorted((DASHBOARD_DIR / "sage_dashboard" / "static").glob("*.js"))
    return [f for f in files if f.name != "queries.py"]


@pytest.mark.parametrize("path", app_code_files(), ids=lambda p: p.name)
def test_no_sql_outside_queries_module(path):
    text = path.read_text(encoding="utf-8")
    assert not SQL_PATTERN.search(text), f"SQL found in {path.name}"
    assert ".execute(" not in text and "executescript" not in text


def test_queries_use_only_fixed_sql_strings():
    """Every execute() call gets a literal string, never one built at run time."""
    tree = ast.parse((DASHBOARD_DIR / "sage_dashboard" / "queries.py").read_text(encoding="utf-8"))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and n.func.attr in ("execute", "executemany", "executescript")]
    assert calls
    for call in calls:
        sql = call.args[0]
        if call.func.attr == "executescript":
            assert isinstance(sql, ast.Name) and sql.id == "schema_sql"  # the contents of schema.sql
            continue
        assert isinstance(sql, ast.Constant) and isinstance(sql.value, str), \
            f"line {call.lineno}: SQL must be a fixed string"


def test_schema_only_comes_from_schema_sql():
    text = (DASHBOARD_DIR / "sage_dashboard" / "queries.py").read_text(encoding="utf-8")
    assert "CREATE TABLE" not in text and "ALTER TABLE" not in text


def test_init_db_upgrades_a_version_2_database_without_losing_data(tmp_path):
    """Databases set up before the live demo existed gain pipeline_log on init-db."""
    old = tmp_path / "v2.sqlite3"
    v2_schema = (DASHBOARD_DIR / "schema.sql").read_text(encoding="utf-8")
    v2_schema = v2_schema[:v2_schema.index("-- Technical log written by the live demo")] + "PRAGMA user_version = 2;"
    raw = sqlite3.connect(old)
    raw.executescript(v2_schema)
    raw.close()
    with pytest.raises(queries.DatabaseNotReady):
        queries.connect(old)  # the app asks for init-db instead of failing later
    queries.create_database(old)
    conn = queries.connect(old)
    assert "pipeline_log" in queries.list_tables(conn)
    conn.close()
