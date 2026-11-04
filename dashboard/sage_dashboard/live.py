"""Live updates for open dashboards.

The database keeps one counter (data_version.revision) that triggers in
schema.sql raise whenever events or people change. Open pages learn about
a new revision in one of two ways:

- /live/stream: Server-Sent Events. Wakes at once when this process
  stores something (see `notify`) and otherwise checks the counter every
  LIVE_CHECK_SECONDS, so changes written by another program are seen too.
  Each stream ends after LIVE_STREAM_SECONDS and the browser reconnects,
  which keeps threads from piling up on a small device.
- /live/revision: one JSON answer, for the browser's polling fallback.

Neither request counts as the person using the dashboard, so they do not
hold off the inactivity sign-out.
"""

import json
import threading
import time

from flask import Blueprint, Response, current_app, jsonify

from . import get_db, queries
from . import presenters as p

bp = Blueprint("live", __name__, url_prefix="/live")


class _Notifier:
    def __init__(self):
        self._cond = threading.Condition()
        self._counter = 0

    def notify(self):
        with self._cond:
            self._counter += 1
            self._cond.notify_all()

    def wait(self, seen, timeout):
        """Wait until notified after `seen`, or timeout. Returns the latest counter."""
        with self._cond:
            if self._counter == seen:
                self._cond.wait(timeout)
            return self._counter


notifier = _Notifier()


def notify():
    notifier.notify()


def _payload(revision):
    tz = p.get_tz(current_app.config["TIMEZONE"])
    return {"revision": revision, "time": p.clock_now(tz)}


@bp.get("/revision")
def revision():
    return jsonify(_payload(queries.get_revision(get_db())))


@bp.get("/stream")
def stream():
    cfg = current_app.config
    db_path = cfg["DATABASE"]
    check_every = cfg["LIVE_CHECK_SECONDS"]
    lifetime = cfg["LIVE_STREAM_SECONDS"]
    retry_ms = cfg["LIVE_RETRY_MS"]
    tz = p.get_tz(cfg["TIMEZONE"])

    def events():
        conn = queries.connect(db_path)
        try:
            yield f"retry: {int(retry_ms)}\n\n"
            last = None
            seen = notifier.wait(-1, 0)
            deadline = time.monotonic() + lifetime
            quiet_since = time.monotonic()
            while time.monotonic() < deadline:
                rev = queries.get_revision(conn)
                if rev != last:
                    last = rev
                    data = json.dumps({"revision": rev, "time": p.clock_now(tz)})
                    yield f"event: update\ndata: {data}\n\n"
                    quiet_since = time.monotonic()
                elif time.monotonic() - quiet_since >= 15:
                    data = json.dumps({"revision": rev, "time": p.clock_now(tz)})
                    yield f"event: ping\ndata: {data}\n\n"
                    quiet_since = time.monotonic()
                seen = notifier.wait(seen, check_every)
        finally:
            conn.close()

    return Response(events(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
