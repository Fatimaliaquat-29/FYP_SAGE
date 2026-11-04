# S.A.G.E. care dashboard

A small, fully local web dashboard that shows a family caregiver how the
person they look after is doing. It shows the current status, possible
falls and walking (gait) risk over time, and updates live as new events
arrive. There are placeholders for sleep and medication.

- Python + Flask, server-rendered templates, plain CSS and a small vanilla JS file. No build step.
- SQLite through Python's built-in `sqlite3` module, with plain parameterised SQL.
- Nothing is loaded from or sent to the internet. No video, frames or images are stored, only text records.

## Set up and run

Python already includes SQLite, so there is nothing extra to install for the
dashboard. If you also want to look inside the database yourself, install
the SQLite command-line tool (`winget install SQLite.SQLite` on Windows,
`sudo apt install sqlite3` on the Jetson). The dashboard does not need it.

From the repository root, with the project venv active:

```
pip install -r dashboard/requirements.txt
python dashboard/manage.py init-db            # creates the database from schema.sql, plus secret keys
python dashboard/manage.py create-user        # asks for a username, name, role and password
python dashboard/manage.py load-sample        # optional: the sample person and their history
python dashboard/manage.py run                # http://127.0.0.1:5000
```

`init-db` is safe to run again: it never deletes data or replaces keys.

### Live video demo (the real pipeline, on a looping video)

One command starts the dashboard AND a background thread that loops a local
video through the existing S.A.G.E. pipeline (MediaPipe pose, the heuristic
fall detection OR-ed with the LSTM, the GAIT walking-risk score, and YOLO
object detection):

```
python dashboard/manage.py create-user        # once, if nobody can sign in yet
python dashboard/manage.py demo               # or: demo --video "test_footage/Sanawar Testing 7-22-26/Forward_fall.mp4"
```

Open http://127.0.0.1:5000/demo and sign in. The page has three tabs:
**Live monitoring** (the processed video with the pipeline's own overlays,
posture, fall signal, gait risk, objects, speed), **Event log** (new events appear by
themselves) and **System status** (which components are running, event
counts, latest event). `demo` sets up the database if needed (it is safe on
an existing one) and adds the sample person, whom the fall alerts are about.

How it works:

- `sage_dashboard/demo_service.py` loads the models once and runs one worker
  thread for the life of the server. Pages only read from it: the latest
  annotated frame (kept in memory, never saved), a status snapshot, and the
  database. Opening, refreshing, switching tabs or closing the page never
  starts, pauses or restarts processing; the video view simply disconnects
  while another tab is shown and reconnects to the current frame.
- Model loading, per-frame classification and overlays are the functions in
  `realtime_fall_detection.py` and `src/posture/pipeline_utils.py`, unchanged.
  The fall alert uses that script's debounce (4 of the last 12 frames, then
  latched for 5 s); a test checks the two give identical alerts.
- GAIT (`src/gait/gait_stream.py`) is wired the way `realtime_fall_detection.py`
  wired it at commit `c3bd40a`: same pose rows plus MediaPipe's 3D world
  landmarks, a 150-frame window re-scored every 15 frames, and a torso
  baseline taken from the first 60 frames of steady standing. It is a
  separate signal: it never feeds the fall alert, and if it fails, fall
  detection carries on and the status tab shows the problem. Each pass
  through the clip starts gait again, so nothing is scored until 150 frames
  in. The default clip is short and mostly not walking, so its scores come
  back "not measurable"; for real scores try
  `--video "test_footage/GAIT_Analysis_Test_Footages/Lateral_Walk.mov"`.
- Events go to the `pipeline_log` table: `fall_alert`, `possible_fall` (a
  fall signal that did not reach the alert rule; one per burst),
  `person_detected` and `person_left` (YOLO person box gone for 2 s), and
  `gait_risk` (the first gait score of a pass, then each change of band:
  low below 0.4, medium to 0.7, high above, as on the caregiver pages). Fall
  alerts are also stored as caregiver events through the same data-source
  layer as `POST /api/events`, so the caregiver pages update live too. Gait
  scores stay in the demo log: a looping clip is not a real day's walking.
- Every frame is processed with the clip's own timestamps, so detection
  matches the offline evaluation. On a CPU this is slower than the video
  (about 7 fps against 30 fps on the development laptop), so playback runs
  at roughly a quarter speed; skipping frames to keep up would change what
  the LSTM sees, so it is not done. When the clip ends it starts again as a
  fresh session.

Options: `--video FILE`, `--no-lstm`, `--no-objects`, `--no-gait`, `--object-model FILE`,
`--patient ID`, `--host`, `--port`.

### Watch it update live without video (event replay)

`demo_replay.py` sends the sample events to the dashboard one at a time,
without any video processing:

```
python dashboard/manage.py --db dashboard/instance/demo.sqlite3 init-db
python dashboard/manage.py --db dashboard/instance/demo.sqlite3 create-user
python dashboard/manage.py --db dashboard/instance/demo.sqlite3 load-sample --patient-only
python dashboard/manage.py --db dashboard/instance/demo.sqlite3 run       # window 1: sign in and open the person's page
python dashboard/demo_replay.py --delay 4              # window 2
```

### All commands

| Command | What it does |
| --- | --- |
| `init-db` | Apply `schema.sql` to the database (creating it) and create `instance/secrets.json` if missing. |
| `create-user [--username U --name N --role caregiver\|admin]` | Add someone who can sign in. The password is asked for twice and not shown. |
| `set-password USERNAME` | Give someone a new password. This also lifts a sign-in lockout. |
| `list-users` | Show who can sign in. |
| `load-sample [--patient-only]` | Load `sample_data/sample_events.json`. |
| `import FILE` | Add a results file from the command line. |
| `new-api-key` | Make a new key for the pipeline and print it. |
| `run [--host 0.0.0.0] [--port 5000]` | Start the dashboard. Use `--host 0.0.0.0` to reach it from other devices on the home network. |
| `demo [--video FILE] [...]` | Start the dashboard with live video processing (see above). |

Put `--db PATH` before any command to use a different database file.

## Configuration and secrets

No secret is written in the code. Each setting is read from an environment
variable first, then from `dashboard/instance/secrets.json`, which `init-db`
creates with random values. That file is git-ignored; keep it private.

| Variable | Meaning |
| --- | --- |
| `SAGE_SECRET_KEY` | Signs the sign-in cookie. |
| `SAGE_API_KEY` | Key the pipeline must send to `POST /api/events`. It is separate from user passwords. |
| `SAGE_DASHBOARD_DB` | Database file (default `dashboard/instance/sage_dashboard.sqlite3`). |
| `SAGE_INSTANCE_DIR` | Folder for the database and `secrets.json`. |
| `SAGE_TIMEZONE` | Display time zone, e.g. `Asia/Karachi` (default: the device's own). |
| `SAGE_SESSION_IDLE_MINUTES` | Sign out after this long without use (default 60). |

## Users and security

- There are two roles. **caregiver** can view everything and mark events as checked (and undo that). **admin** can also add result files and manage who can sign in (the "Who can sign in" page).
- Passwords are stored only as Werkzeug salted hashes (scrypt) and are never logged.
- A failed sign-in never says whether the username or the password was wrong. After 5 wrong attempts for a name within 15 minutes, that name is paused for 5 minutes. This applies to names that don't exist too, so it reveals nothing.
- Sessions use an HTTP-only, SameSite=Strict cookie and end after `SAGE_SESSION_IDLE_MINUTES` without use. Background live updates do not count as use, so an unattended screen signs out and says so clearly. It does not silently go stale.
- Every form and state-changing request carries a CSRF token. The only exception is `POST /api/events`, which uses the API key and accepts no cookie.
- The cookie is not marked `Secure` because the dashboard is served over plain HTTP on the home network. Put it behind HTTPS before using it anywhere else.

## Live updates

`schema.sql` keeps one counter, `data_version.revision`, which triggers raise
whenever events or people change. Open pages watch it like this:

1. **Server-Sent Events** (`/live/stream`). The stream wakes immediately when this server stores something, and checks the counter every 2 seconds so writes from another program are noticed too. Each stream lasts 5 minutes, then the browser reconnects, so threads don't pile up on the Jetson.
2. **Polling** (`/live/revision`) every 10 seconds. This is used if the stream fails three times or the browser lacks EventSource. The page tries the stream again later.

When the counter changes, the page fetches itself again and swaps in only the
parts that changed (status box, alerts, chart, latest news, results list).
Keyboard focus stays where it was. A "Live" or "Reconnecting…" label and an
"Updated" time are shown, and new alerts are announced to screen readers. If
the session has ended, the page says so and offers "Sign in again"; what was
on screen stays readable.

## Sending events: `POST /api/events`

```
POST /api/events
Authorization: Bearer <SAGE_API_KEY>        (or  X-API-Key: <key>)
Content-Type: application/json

{"event_id": "cam1-000123", "patient": "P001", "timestamp": "2026-11-02T15:42:00+05:00",
 "type": "fall", "confidence": 0.91}
```

The body is either one event object (the same fields as the import file), or
the full import format below for a batch or to add people. Every field is
validated, and the body is limited to 64 KB. Responses:

| Status | Meaning |
| --- | --- |
| `201` | Stored. |
| `200` | Already stored (duplicate `event_id`), or people only. |
| `400` | Not JSON or empty. |
| `401` | Missing or wrong key. |
| `413` | Too large. |
| `415` | Not `application/json`. |
| `422` | Nothing valid. `problems` lists each field. |
| `503` | No key configured. |

## Import file format

One UTF-8 JSON object per file:

```json
{
  "format_version": 1,
  "patients": [
    {"id": "P001", "name": "Amina Rahman", "preferred_name": "Nani", "age": 81, "room": "Ground-floor bedroom"}
  ],
  "events": [
    {"event_id": "Normal_Fall_2:f287", "patient": "P001",
     "timestamp": "2026-11-01T15:42:00+05:00", "type": "fall",
     "confidence": 0.91, "source": "video:Normal_Fall_2.mp4",
     "details": {"method": "hybrid", "frame": 287}},
    {"event_id": "walk_2026-11-02", "patient": "P001",
     "timestamp": "2026-11-02T10:05:00+05:00", "type": "gait_risk",
     "confidence": 0.8, "risk_score": 0.46}
  ]
}
```

**patients** (optional; send each person once, and sending them again updates their details)

| Field | Required | Notes |
| --- | --- | --- |
| `id` | yes | Your identifier for the person (up to 64 characters). |
| `name` | yes | Full name. |
| `preferred_name` | no | What the family calls them, used in sentences and buttons ("I've checked on Nani"). If missing, the first name is used. |
| `age` | no | Whole number from 0 to 130. |
| `room` | no | Where the camera is. |

**events**

| Field | Required | Notes |
| --- | --- | --- |
| `patient` | yes | A patient `id` from this file or one added earlier. |
| `timestamp` | yes | ISO 8601. Include the offset. Without one, it is read as this device's local time. More than one day in the future is rejected. |
| `type` | yes | `fall` or `gait_risk`. |
| `confidence` | yes | 0 to 1. |
| `risk_score` | for `gait_risk` | 0 to 1, from `GaitRiskAssessor.assess_risk()["risk_score"]`. |
| `severity` | no | `low`, `medium` or `high`. If missing, falls are `high`; for gait, a risk below 0.4 is `low`, 0.4 to 0.7 is `medium`, and 0.7 or above is `high`. |
| `event_id` | recommended | A stable id. Sending the same id again is skipped. Without one, an event is a duplicate when its patient, timestamp and type all match. |
| `source`, `description`, `details` | no | `description` replaces the built-in wording. `details` is any JSON object up to 10 KB, and must never contain images. |

Bad records are reported (in plain words on screen, and in technical detail
from the API and command line) and skipped; valid ones are still stored.

## Database

`schema.sql` is the single source of truth: tables `patients`, `users`,
`login_failures`, `imports`, `events` (including `checked_at` and
`checked_by`, which record who pressed "I've checked" and when) and
`data_version`, plus `pipeline_log` for the live video demo (schema version
3; running `init-db` on an older database adds it without touching data),
plus indexes, CHECK constraints and foreign keys. It is
commented column by column. All SQL is in `sage_dashboard/queries.py` as
fixed, parameterised strings. Optional filters use
`(:x IS NULL OR col = :x)` and lists are passed through `json_each`, so no
SQL is built at run time. If the database is missing or was not set up,
every page shows a friendly "not ready yet" message instead of an error.

## Tests

```
pip install -r dashboard/requirements.txt
python -m playwright install chromium     # once, for the browser tests
cd dashboard
python -m pytest
```

Each test uses a temporary database built from `schema.sql` and a temporary
instance folder, so the real database and keys are never touched.

## Not built yet

- Connecting the real SAGE pipeline. It needs to `POST` each event to `/api/events` with the API key; nothing else changes.
- Sleep monitoring and medication. The overview shows "Not available yet" cards in their place.
- HTTPS and a production WSGI server, for use outside a single home network.
