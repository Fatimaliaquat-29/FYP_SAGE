"""Demo: replay the sample events into a running dashboard, one at a time.

The SAGE pipeline is not connected yet. This script stands in for it: it
sends each sample event to POST /api/events with a pause in between, so you
can watch an open dashboard update by itself.

    python dashboard/manage.py run                 (in one window)
    python dashboard/demo_replay.py                (in another)

Times are shifted so the last event happens "now", and each run uses fresh
event ids, so the events show up as new every time. Use --keep-times to send
the sample exactly as written (a second run then adds nothing: duplicates).
Uses the same API key as the dashboard (SAGE_API_KEY or instance/secrets.json).
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

DASHBOARD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DASHBOARD_DIR))

from sage_dashboard import config  # noqa: E402

SAMPLE_FILE = DASHBOARD_DIR / "sample_data" / "sample_events.json"


def _post(url, key, body):
    request = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(request, timeout=10) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, json.loads(exc.read() or b"{}")
        except ValueError:
            return exc.code, {}


def shifted_events(events, keep_times, now=None):
    """Move the events so the newest one happens now, with fresh ids."""
    if keep_times:
        return events
    now = now or datetime.now(timezone.utc)
    times = [datetime.fromisoformat(e["timestamp"]) for e in events]
    offset = now - max(times)
    run = uuid.uuid4().hex[:8]
    out = []
    for event, when in zip(events, times):
        e = dict(event)
        e["timestamp"] = (when + offset).isoformat()
        e["event_id"] = f"demo-{run}-{event.get('event_id', len(out))}"
        e["source"] = "demo replay"
        out.append(e)
    return out


def main(argv=None, sleep=time.sleep):
    parser = argparse.ArgumentParser(description="Replay sample events into a running dashboard.")
    parser.add_argument("--url", default="http://127.0.0.1:5000", help="where the dashboard is running")
    parser.add_argument("--delay", type=float, default=4.0, help="seconds between events")
    parser.add_argument("--file", type=Path, default=SAMPLE_FILE, help="events file in the import format")
    parser.add_argument("--keep-times", action="store_true", help="send the original times and ids")
    parser.add_argument("--api-key", default=None, help="defaults to SAGE_API_KEY or instance/secrets.json")
    args = parser.parse_args(argv)

    key = args.api_key or config.load_api_key()
    if not key:
        print("No API key found. Run: python dashboard/manage.py init-db", file=sys.stderr)
        return 2
    endpoint = args.url.rstrip("/") + "/api/events"
    data = json.loads(args.file.read_text(encoding="utf-8"))

    try:
        status, body = _post(endpoint, key, {"format_version": 1, "patients": data.get("patients", []),
                                             "events": []})
    except urllib.error.URLError:
        print(f"Cannot reach the dashboard at {args.url}. Is it running? "
              "(python dashboard/manage.py run)", file=sys.stderr)
        return 1
    if status == 401:
        print("The dashboard did not accept the API key.", file=sys.stderr)
        return 1
    if status >= 400:
        print(f"Could not add the people from the sample ({status}): {body.get('message')}", file=sys.stderr)
        return 1

    events = sorted(shifted_events(data["events"], args.keep_times), key=lambda e: e["timestamp"])
    print(f"Sending {len(events)} events to {endpoint}, one every {args.delay:g} seconds. "
          "Watch the dashboard. Press Ctrl+C to stop.")
    for i, event in enumerate(events, start=1):
        if i > 1:
            sleep(args.delay)
        try:
            status, body = _post(endpoint, key, event)
        except urllib.error.URLError:
            print("Lost contact with the dashboard.", file=sys.stderr)
            return 1
        outcome = {201: "added", 200: "already there"}.get(status, f"refused ({status}: {body.get('message')})")
        print(f"[{i}/{len(events)}] {event['type']:<9} {event['timestamp']}  {outcome}")
    print("Done.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nStopped.")
