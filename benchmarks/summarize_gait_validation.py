"""
benchmarks/summarize_gait_validation.py
=========================================
Turns benchmarks/gait_footage_validation_results.json (written by
validate_gait_on_footage.py) into a markdown summary table + a flagged
anomalies section. Read-only; does not touch src/gait/ or any other
production code.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _fmt(x, nd=3):
    if x is None:
        return "-"
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def summarize(results_path: str) -> str:
    with open(results_path) as f:
        results = json.load(f)

    lines = []
    flags = []

    lines.append("| File | Frames | FPS | Time-to-1st-assess (s) | # assessments | Risk range | Latency mean/max (ms) | 1st-call latency (ms) | Old-vs-new mismatches | Threaded==Streaming | Ankle vis. | Hip vis. |")
    lines.append("|---|---:|---:|---:|---:|---|---:|---:|---:|---|---:|---:|")

    for e in results:
        name = e["name"]
        if e.get("error"):
            lines.append(f"| {name} | ERROR | | | | | | | | | | |")
            flags.append(f"**{name}**: crashed -- `{e['error'].splitlines()[0]}`")
            continue
        if e.get("skipped_reason"):
            lines.append(f"| {name} | {e.get('n_frames','-')} | {_fmt(e.get('fps'),1)} | SKIPPED: {e['skipped_reason']} | | | | | | | | |")
            continue

        s = e["streaming"]
        tp = e["threaded_pipeline"]
        vis = e.get("raw_visibility", {})

        scores = [a["risk_score"] for a in s["assessments"] if a["risk_score"] is not None]
        risk_range = f"{min(scores):.2f}-{max(scores):.2f}" if scores else "all None"

        mismatches = sum(1 for p in s["parity_checks"] if p.get("value_mismatches") or not p.get("score_match", True) or "error" in p)
        n_checks = len(s["parity_checks"])

        lat_mean = s.get("assessment_latency_ms_mean_excl_first")
        lat_max = s.get("assessment_latency_ms_max_excl_first")
        lat_str = f"{_fmt(lat_mean,2)}/{_fmt(lat_max,2)}" if lat_mean is not None else ("n/a (1 assess.)" if s["n_assessments"] else "-")

        lines.append(
            f"| {name} | {e['n_frames']} | {_fmt(e['fps'],1)} | {_fmt(s['time_to_first_assessment_sec'],2)} "
            f"| {s['n_assessments']} | {risk_range} | {lat_str} | {_fmt(s.get('first_assessment_latency_ms'),1)} "
            f"| {mismatches}/{n_checks} | {e.get('threaded_matches_streaming_count')} "
            f"| {_fmt(vis.get('ankle_valid_ratio'),2)} | {_fmt(vis.get('hip_valid_ratio'),2)} |"
        )

        # ---- Flag anomalies ----
        if mismatches > 0:
            flags.append(f"**{name}**: {mismatches}/{n_checks} old-vs-new parity CHECKS DIFFERED -- needs investigation.")
        if e.get("threaded_matches_streaming_count") is False:
            flags.append(f"**{name}**: threaded pipeline produced {tp['n_results']} results vs {s['n_assessments']} from direct streaming on identical frames (paced at real fps) -- possible threading/queue bug.")
        if tp.get("errors"):
            flags.append(f"**{name}**: threaded pipeline raised: {tp['errors']}")
        if not tp.get("clean_stop", True):
            flags.append(f"**{name}**: GaitPipeline.stop() did not join cleanly.")

        jit = e.get("threaded_pipeline_jitter")
        if jit is not None:
            if jit.get("errors"):
                flags.append(f"**{name}** (jitter sim): raised: {jit['errors']}")
            if not jit.get("clean_stop", True):
                flags.append(f"**{name}** (jitter sim): stop() did not join cleanly under simulated camera jitter/drops.")

        # Flicker check: consecutive non-None risk scores swinging wildly
        # frame-to-frame within a short window is what a user would perceive
        # as an alarming/confusing oscillating label.
        non_none = [(a["frame_idx"], a["risk_score"]) for a in s["assessments"] if a["risk_score"] is not None]
        if len(non_none) >= 3:
            diffs = [abs(non_none[i][1] - non_none[i - 1][1]) for i in range(1, len(non_none))]
            if max(diffs) > 0.35:
                flags.append(f"**{name}**: risk_score jumped by {max(diffs):.2f} between consecutive reassessments (frames {non_none[diffs.index(max(diffs))][0]}->{non_none[diffs.index(max(diffs))+1][0]}) -- check for flicker.")

        # Low-visibility edge case: confirm unavailable != silently-scored.
        if vis.get("ankle_valid_ratio", 1.0) < 0.5:
            stride_available = [a["signals"]["stride_regularity"]["available"] for a in s["assessments"]]
            if any(stride_available):
                flags.append(f"**{name}**: ankle visibility {vis['ankle_valid_ratio']:.2f} (<0.5) yet stride_regularity was 'available' in at least one assessment -- verify this is a legitimate partial-window recovery, not a leak.")
            else:
                pass  # expected: correctly reported unavailable, not flagged

    md = "\n".join(lines)
    if flags:
        md += "\n\n## Flags / anomalies\n\n" + "\n".join(f"- {f}" for f in flags)
    else:
        md += "\n\n## Flags / anomalies\n\nNone.\n"
    return md


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="benchmarks/gait_footage_validation_results.json")
    args = ap.parse_args()
    print(summarize(args.input))
