-- S.A.G.E. care dashboard: database schema.
--
-- This file is the single source of truth for the database structure.
-- The application never creates or changes tables itself; it only runs
-- this file through `python dashboard/manage.py init-db`.
--
-- Running it again on an existing database is safe: every statement uses
-- IF NOT EXISTS or OR IGNORE, so existing data is left alone.
--
-- Times are stored as UTC text in one fixed format, "YYYY-MM-DDTHH:MM:SSZ",
-- so plain text comparison sorts them correctly.
-- No video, frames or images are ever stored: only short text records.

-- People being looked after.
CREATE TABLE IF NOT EXISTS patients (
    id             INTEGER PRIMARY KEY,                -- internal id, used in page addresses
    external_id    TEXT    NOT NULL UNIQUE             -- id used by the analysis software / import files
                   CHECK (length(external_id) BETWEEN 1 AND 64),
    name           TEXT    NOT NULL                    -- full name shown on the dashboard
                   CHECK (length(name) BETWEEN 1 AND 100),
    preferred_name TEXT                                -- what the family calls them, e.g. "Nani" (optional)
                   CHECK (preferred_name IS NULL OR length(preferred_name) BETWEEN 1 AND 50),
    age            INTEGER                             -- age in years (optional)
                   CHECK (age IS NULL OR age BETWEEN 0 AND 130),
    room           TEXT                                -- where the camera is, e.g. "Bedroom" (optional)
                   CHECK (room IS NULL OR length(room) <= 100),
    created_at     TEXT    NOT NULL,                   -- when the person was first added (UTC)
    updated_at     TEXT    NOT NULL                    -- when their details last changed (UTC)
);

-- People who can sign in to the dashboard.
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY,
    username      TEXT    NOT NULL UNIQUE               -- sign-in name, always lower case
                  CHECK (length(username) BETWEEN 3 AND 32 AND username = lower(username)),
    display_name  TEXT    NOT NULL                      -- name shown on screen, e.g. "Sara"
                  CHECK (length(display_name) BETWEEN 1 AND 60),
    password_hash TEXT    NOT NULL                      -- salted hash from Werkzeug; never the password itself
                  CHECK (length(password_hash) >= 20),
    role          TEXT    NOT NULL                      -- 'caregiver': view and mark as checked;
                  CHECK (role IN ('caregiver', 'admin')),  -- 'admin': also add results and manage users
    created_at    TEXT    NOT NULL,                     -- when the account was made (UTC)
    last_login_at TEXT                                  -- last successful sign-in (UTC), NULL if never
);

-- Failed sign-in attempts, used for a short lockout. Keyed by the name that
-- was typed (which may not be a real user), so a lockout never reveals
-- whether an account exists.
CREATE TABLE IF NOT EXISTS login_failures (
    username        TEXT    PRIMARY KEY                 -- lower-cased name as typed
                    CHECK (length(username) BETWEEN 1 AND 64),
    failures        INTEGER NOT NULL CHECK (failures >= 0),  -- failed attempts in the current window
    first_failed_at TEXT    NOT NULL,                   -- start of the current counting window (UTC)
    locked_until    TEXT                                -- no sign-in allowed before this time (UTC), or NULL
);

-- History of uploaded result files (live events are not logged here).
CREATE TABLE IF NOT EXISTS imports (
    id          INTEGER PRIMARY KEY,
    source      TEXT    NOT NULL,                       -- e.g. "file:results.json"
    imported_at TEXT    NOT NULL,                       -- when the upload happened (UTC)
    imported_by INTEGER REFERENCES users(id) ON DELETE SET NULL,  -- who uploaded it (NULL: command line)
    added       INTEGER NOT NULL DEFAULT 0 CHECK (added >= 0),       -- new events stored
    duplicates  INTEGER NOT NULL DEFAULT 0 CHECK (duplicates >= 0),  -- events already present, skipped
    rejected    INTEGER NOT NULL DEFAULT 0 CHECK (rejected >= 0),    -- records that could not be read
    error       TEXT                                    -- why the whole file was refused, if it was
);

-- Things the cameras noticed: possible falls and walking (gait) checks.
CREATE TABLE IF NOT EXISTS events (
    id           INTEGER PRIMARY KEY,
    patient_id   INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,  -- who it is about
    dedupe_key   TEXT    NOT NULL UNIQUE,               -- stable identity; a repeat is skipped, not stored twice
    occurred_at  TEXT    NOT NULL,                      -- when it happened (UTC)
    type         TEXT    NOT NULL                       -- 'fall' or 'gait_risk'
                 CHECK (type IN ('fall', 'gait_risk')),
    severity     TEXT    NOT NULL                       -- 'high' = Urgent, 'medium' = Worth a look,
                 CHECK (severity IN ('low', 'medium', 'high')),  -- 'low' = For information
    confidence   REAL    NOT NULL                       -- 0-1, how sure the analysis was
                 CHECK (confidence BETWEEN 0 AND 1),
    risk_score   REAL                                   -- 0-1 walking risk; only for 'gait_risk'
                 CHECK (risk_score IS NULL OR risk_score BETWEEN 0 AND 1),
    source       TEXT    NOT NULL,                      -- where it came from, e.g. "video:clip07.mp4" or "live"
    description  TEXT,                                  -- optional plain-language text to show instead of ours
    details_json TEXT    NOT NULL DEFAULT '{}',         -- extra analysis values as JSON text (never images)
    checked_at   TEXT,                                  -- when someone pressed "I've checked" (UTC), NULL if not yet
    checked_by   INTEGER REFERENCES users(id) ON DELETE SET NULL,  -- who pressed it
    import_id    INTEGER REFERENCES imports(id) ON DELETE SET NULL, -- which upload it came in (NULL: live)
    created_at   TEXT    NOT NULL,                      -- when it was stored (UTC)
    CHECK (checked_by IS NULL OR checked_at IS NOT NULL)
);

-- Indexes for the filters the dashboard uses.
CREATE INDEX IF NOT EXISTS idx_events_patient_time      ON events (patient_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_events_patient_type_time ON events (patient_id, type, occurred_at);
CREATE INDEX IF NOT EXISTS idx_events_patient_sev_time  ON events (patient_id, severity, occurred_at);
CREATE INDEX IF NOT EXISTS idx_events_patient_checked   ON events (patient_id, checked_at, severity);
CREATE INDEX IF NOT EXISTS idx_imports_time             ON imports (imported_at);

-- A single counter that goes up whenever events or people change. Open
-- dashboards watch it to know when to refresh, even when the change came
-- from another program writing to the same database file.
CREATE TABLE IF NOT EXISTS data_version (
    id       INTEGER PRIMARY KEY CHECK (id = 1),        -- always exactly one row
    revision INTEGER NOT NULL DEFAULT 0 CHECK (revision >= 0)
);
INSERT OR IGNORE INTO data_version (id, revision) VALUES (1, 0);

CREATE TRIGGER IF NOT EXISTS trg_events_insert AFTER INSERT ON events
BEGIN UPDATE data_version SET revision = revision + 1 WHERE id = 1; END;
CREATE TRIGGER IF NOT EXISTS trg_events_update AFTER UPDATE ON events
BEGIN UPDATE data_version SET revision = revision + 1 WHERE id = 1; END;
CREATE TRIGGER IF NOT EXISTS trg_events_delete AFTER DELETE ON events
BEGIN UPDATE data_version SET revision = revision + 1 WHERE id = 1; END;
CREATE TRIGGER IF NOT EXISTS trg_patients_insert AFTER INSERT ON patients
BEGIN UPDATE data_version SET revision = revision + 1 WHERE id = 1; END;
CREATE TRIGGER IF NOT EXISTS trg_patients_update AFTER UPDATE ON patients
BEGIN UPDATE data_version SET revision = revision + 1 WHERE id = 1; END;
CREATE TRIGGER IF NOT EXISTS trg_patients_delete AFTER DELETE ON patients
BEGIN UPDATE data_version SET revision = revision + 1 WHERE id = 1; END;

-- Technical log written by the live demo (manage.py demo): everything the
-- background video processing noticed, including things that are not
-- caregiver alerts (a person coming into or leaving view, a short fall
-- signal that did not become an alert). Confirmed fall alerts are ALSO
-- stored in `events` above, where the caregiver pages show them.
-- Text only: no frames or snapshots are stored.
CREATE TABLE IF NOT EXISTS pipeline_log (
    id           INTEGER PRIMARY KEY,
    occurred_at  TEXT    NOT NULL,                      -- when it was noticed (UTC, wall clock)
    type         TEXT    NOT NULL                       -- what was noticed
                 CHECK (type IN ('person_detected', 'person_left', 'possible_fall', 'fall_alert', 'gait_risk')),
    confidence   REAL                                   -- 0-1 from the detector or heuristic, if any
                 CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1),
    source       TEXT    NOT NULL,                      -- the video being processed, e.g. "Forward_fall.mp4"
    video_time   REAL    CHECK (video_time IS NULL OR video_time >= 0),  -- seconds into the clip
    frame        INTEGER CHECK (frame IS NULL OR frame >= 0),            -- frame number within the clip
    loop_number  INTEGER NOT NULL DEFAULT 1 CHECK (loop_number >= 1),    -- which pass through the clip
    details_json TEXT    NOT NULL DEFAULT '{}'          -- posture, heuristic labels, counts, gait score (JSON text)
);
CREATE INDEX IF NOT EXISTS idx_pipeline_log_time ON pipeline_log (occurred_at);
CREATE INDEX IF NOT EXISTS idx_pipeline_log_type ON pipeline_log (type, occurred_at);

-- Version of this schema. The app refuses (politely) to run on a database
-- set up with a different version. Running init-db on a version 2
-- database adds pipeline_log and moves it to version 3; nothing is lost.
PRAGMA user_version = 3;
