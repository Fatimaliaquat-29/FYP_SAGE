"""STAGE 6 gate for C. Writes raw/gate.json {run_C, conditions...}. Exit 0 always (decision is in the file)."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import RAW, log, write_json, read_json, run_start, now, decision

SETS = ("heldout_objects", "heldout_objects_rotfix", "reserved388_partial", "round6_heldout")


def main():
    g = {"evaluated_at": now().isoformat(timespec="seconds"), "conditions": {}, "run_C": False}
    s1 = read_json(RAW / "stage1_control.json", {})
    sb = read_json(RAW / "scores__B_yolo26n_30ep.json", {})
    ok_recall = True
    rows = []
    for s in SETS:
        for thr in ("0.5", "0.3"):
            try:
                a = s1["scores"][f"A_v7|{s}"]["by_iou"][thr]["person"]
                b = sb["scores"][f"{s}|c0.4"]["by_iou"][thr]["person"]
                passed = b["recall"] >= a["recall"] - 0.02 - 1e-12
                rows.append({"set": s, "iou": thr, "A": f"{a['tp']}/{a['n_gt']}={a['recall']:.3f}",
                             "B": f"{b['tp']}/{b['n_gt']}={b['recall']:.3f}", "pass": passed})
                ok_recall &= passed
            except Exception as e:
                rows.append({"set": s, "iou": thr, "error": repr(e), "pass": False})
                ok_recall = False
    g["conditions"]["recall_within_0.02_on_each_set"] = {"pass": ok_recall, "rows": rows}
    try:
        a_fp = s1["empty_fp|A_v7"]["fp_rate_pct"]
        b_fp = sb["empty_fp"]["c0.4"]["fp_rate_pct"]
        g["conditions"]["empty_fp_le_A_plus_2pp"] = {"pass": b_fp <= a_fp + 2.0, "A_pct": a_fp, "B_pct": b_fp}
    except Exception as e:
        g["conditions"]["empty_fp_le_A_plus_2pp"] = {"pass": False, "error": repr(e)}
    try:
        eps = read_json(RAW / "train_B_yolo26n_30ep_epochs.json", [])
        seen = set()
        eps = [e for e in eps if not (e.get("t_start") in seen or seen.add(e.get("t_start")))]  # final-val callback repeats the last epoch
        durs = [e["duration_s"] for e in eps if e.get("duration_s")]
        mean_s = sum(durs) / len(durs)
        proj = now() + dt.timedelta(seconds=50 * mean_s * 1.1)
        limit = run_start() + dt.timedelta(hours=11.5)
        g["conditions"]["time"] = {"pass": proj <= limit, "B_mean_s_per_epoch": mean_s, "n_epochs_measured": len(durs),
                                   "projected_C_finish": proj.isoformat(timespec="seconds"),
                                   "limit_run_start_plus_11.5h": limit.isoformat(timespec="seconds")}
    except Exception as e:
        g["conditions"]["time"] = {"pass": False, "error": repr(e)}
    failed = [k for k, v in g["conditions"].items() if not v.get("pass")]
    g["run_C"] = not failed
    g["failed_conditions"] = failed
    write_json(RAW / "gate.json", g)
    decision(f"C gate: run_C={g['run_C']}; failed conditions: {failed or 'none'} (details raw/gate.json)")
    log(f"gate: run_C={g['run_C']} failed={failed}")


if __name__ == "__main__":
    main()
