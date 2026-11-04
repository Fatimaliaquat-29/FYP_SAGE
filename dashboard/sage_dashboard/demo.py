"""The live demo page and the read-only endpoints it polls.

Every endpoint only READS from the background service (demo_service.py)
and the database; none of them can start, pause or restart processing.
The data endpoints live under /live/ so that, like the other live
updates, they do not count as the person using the dashboard.
"""

import json

from flask import Blueprint, Response, current_app, jsonify, render_template, request

from . import demo_service, get_db, queries
from . import presenters as p

bp = Blueprint("demo", __name__)

TYPE_LABELS = {
    "fall_alert": "Fall alert",
    "possible_fall": "Possible fall (signal)",
    "person_detected": "Person detected",
    "person_left": "Person left view",
    "gait_risk": "Walking (gait) risk",
}


def _tz():
    return p.get_tz(current_app.config["TIMEZONE"])


def present_pipeline_event(row, tz):
    when = p.local(row["occurred_at"], tz) if row["occurred_at"].endswith("Z") else None
    try:
        details = json.loads(row["details_json"] or "{}")
    except ValueError:
        details = {}
    video_time = row["video_time"] or 0.0
    return {"id": row["id"], "type": row["type"], "label": TYPE_LABELS.get(row["type"], row["type"]),
            "time": p.format_clock(when) if when else row["occurred_at"],
            "seconds": f"{when:%H:%M:%S}" if when else "",
            "occurred_at": row["occurred_at"],
            "confidence": row["confidence"],
            "confidence_percent": round(row["confidence"] * 100) if row["confidence"] is not None else None,
            "video": row["source"], "video_time": f"{int(video_time // 60)}:{video_time % 60:04.1f}",
            "frame": row["frame"], "loop": row["loop_number"], "details": details}


@bp.get("/demo")
def page():
    return render_template("demo.html", type_labels=TYPE_LABELS)


@bp.get("/live/demo/status")
def status():
    service = demo_service.get_service()
    conn = get_db()
    counts = queries.pipeline_event_counts(conn)
    latest = queries.latest_pipeline_event(conn)
    body = service.status() if service is not None else {"state": "not_started"}
    body.update(total_events=sum(counts.values()), counts=counts,
                latest_event=present_pipeline_event(latest, _tz()) if latest else None,
                server_time=p.clock_now(_tz()))
    return jsonify(body)


@bp.get("/live/demo/events")
def events():
    try:
        after = max(0, int(request.args.get("after", 0)))
        limit = min(200, max(1, int(request.args.get("limit", 100))))
    except ValueError:
        return jsonify(error="Bad Request", message="\"after\" and \"limit\" must be whole numbers."), 400
    tz = _tz()
    rows = queries.pipeline_events_after(get_db(), after, limit)
    return jsonify(events=[present_pipeline_event(r, tz) for r in rows])


@bp.get("/live/demo/video.mjpg")
def video():
    service = demo_service.get_service()
    if service is None:
        return jsonify(error="Service Unavailable", message="Video processing is not running."), 503

    def frames():
        seq = 0
        while True:
            seq, jpeg = service.wait_for_frame(seq, timeout=5.0)
            if jpeg is not None:
                yield (b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                       + str(len(jpeg)).encode() + b"\r\n\r\n" + jpeg + b"\r\n")
            if not service.is_running:
                return  # processing ended; the page shows the status
            # A viewer closing the page ends this generator only; the
            # processing thread never notices.

    return Response(frames(), mimetype="multipart/x-mixed-replace; boundary=frame",
                    headers={"Cache-Control": "no-cache, no-store", "X-Accel-Buffering": "no"})
