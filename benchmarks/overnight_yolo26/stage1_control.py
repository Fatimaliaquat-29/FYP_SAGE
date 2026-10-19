"""STAGE 1 -- scoring harness check + control (A = models/yolov8n_sage_merged_v7.pt) reproduction."""
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import RAW, MODELS, OUT, log, write_json, read_json, decision, CONF, IMGSZ
import score_lib as S

REFS = {
    # eval/heldout_objects, conf 0.4 imgsz 640, IoU 0.5 (results/yolo_person_detection/v7_results.md)
    "heldout_objects": {"person_tp": 58, "person_n": 93, "person_fp": 1,
                        "clips": {"With_people_TV_Lounge_1_Fall": (6, 18), "With_people_Bedroom_Fall": (0, 20)}},
    # handlabels/round6_heldout (v7_results.md / v7_suite_iou0.5.md)
    "round6_heldout": {"person_tp": 50, "person_n": 226, "person_fp": 0, "chair_recall": 0.74, "bed_recall": 0.49},
    "empty_fp_pct": 0.0, "empty_frames": 4101,
    # v6 per-clip reference, IoU 0.3 (reserved_heldout_posture_v6.md "Per clip"): (rate, n_boxes, fp)
    "v6_388_per_clip_iou0.3": {
        "With_people_Bedroom_Walk": (1.00, 14, 0), "With_people_TV_Lounge_1_Walk": (1.00, 1, 0),
        "With_people_TV_Lounge_1_Sit": (1.00, 16, 0), "With_people_people": (1.00, 18, 1),
        "With_people_Bedroom_Sit": (1.00, 24, 0), "With_people_people_(2)": (0.94, 32, 0),
        "With_people_Bedroom_Fall": (0.95, 62, 0), "With_people_TV_Lounge_2_Fall": (0.46, 35, 0),
        "With_people_TV_Lounge_2_Fall2": (0.41, 41, 0), "With_people_TV_Lounge_1_Fall2": (0.31, 48, 1),
        "With_people_TV_Lounge_1_Fall": (0.18, 97, 3)},
    "v6_388_overall": {"0.5": (224, 388), "0.3": (227, 388)},
}


def chk(label, measured_tp, measured_n, ref_tp, ref_n, rate_tol=0.02, box_tol=1):
    m = measured_tp / measured_n if measured_n else None
    r = ref_tp / ref_n if ref_n else None
    ok = (measured_n == ref_n and abs(measured_tp - ref_tp) <= box_tol
          and (m is None or r is None or abs(m - r) <= rate_tol + 1e-9))
    return {"check": label, "measured": f"{measured_tp}/{measured_n}", "reference": f"{ref_tp}/{ref_n}",
            "measured_rate": m, "reference_rate": r, "ok": ok}


def main():
    from ultralytics import YOLO
    out = {"conf": CONF, "imgsz": IMGSZ, "scores": {}, "checks": [], "notes": []}
    models = {k: YOLO(str(MODELS[k])) for k in ("A_v7", "v6") if MODELS[k].exists()}
    for key, m in models.items():
        for s in S.EVAL_SETS:
            log(f"S1 scoring {key} on {s}")
            out["scores"][f"{key}|{s}"] = S.score_model_on_set(m, key, s)
            write_json(RAW / "stage1_control.json", out)

    # harness equality: original score_loaded_model vs this harness, A on heldout_objects, person, IoU 0.5
    try:
        gt, _ = S.load_set("heldout_objects")
        orig = S.score_loaded_model(models["A_v7"], gt, CONF, 0.5, {0}, IMGSZ)
        o = orig.get(0, {"tp": 0, "fp": 0, "fn": 0})
        mine = out["scores"]["A_v7|heldout_objects"]["by_iou"]["0.5"]["person"]
        out["harness_equality"] = {"original_score_loaded_model": o, "this_harness": {k: mine[k] for k in ("tp", "fp", "fn")},
                                   "identical": (o["tp"], o["fp"], o["fn"]) == (mine["tp"], mine["fp"], mine["fn"])}
    except Exception as e:
        out["harness_equality"] = {"FAILED": repr(e), "tb": traceback.format_exc()[-2000:]}

    # empty-room FP
    for key, m in models.items():
        log(f"S1 empty-room FP {key}")
        try:
            out[f"empty_fp|{key}"] = S.empty_room_fp(m, key)
        except Exception as e:
            out[f"empty_fp|{key}"] = {"FAILED": repr(e), "tb": traceback.format_exc()[-2000:]}
        write_json(RAW / "stage1_control.json", out)

    # ---- reference checks (A) ----
    a = out["scores"]["A_v7|heldout_objects"]["by_iou"]["0.5"]
    ref = REFS["heldout_objects"]
    out["checks"].append(chk("A heldout_objects person @IoU0.5", a["person"]["tp"], a["person"]["n_gt"], ref["person_tp"], ref["person_n"]))
    out["checks"].append({"check": "A heldout_objects person FP @IoU0.5", "measured": a["person"]["fp"], "reference": ref["person_fp"],
                          "ok": abs(a["person"]["fp"] - ref["person_fp"]) <= 1})
    for clip, (rt, rn) in ref["clips"].items():
        c = a["per_clip_person"].get(clip, {"tp": 0, "n_gt": 0})
        out["checks"].append(chk(f"A heldout_objects {clip} @IoU0.5", c["tp"], c["n_gt"], rt, rn))
    r6 = out["scores"]["A_v7|round6_heldout"]["by_iou"]["0.5"]
    ref = REFS["round6_heldout"]
    out["checks"].append(chk("A round6_heldout person @IoU0.5", r6["person"]["tp"], r6["person"]["n_gt"], ref["person_tp"], ref["person_n"]))
    out["checks"].append({"check": "A round6_heldout person FP @IoU0.5", "measured": r6["person"]["fp"], "reference": ref["person_fp"],
                          "ok": abs(r6["person"]["fp"] - ref["person_fp"]) <= 1})
    for cls, rr in (("chair", ref["chair_recall"]), ("bed", ref["bed_recall"])):
        c = r6["per_class"].get(cls, {})
        m = c.get("recall")
        out["checks"].append({"check": f"A round6_heldout {cls} recall @IoU0.5", "measured": m, "measured_counts": f"{c.get('tp')}/{c.get('n_gt')}",
                              "reference": rr, "ok": m is not None and abs(m - rr) <= 0.02 + 0.005})
    e = out.get("empty_fp|A_v7", {})
    if "FAILED" not in e:
        out["checks"].append({"check": "A empty-room FP rate (Reserved/Empty, every frame)", "measured": f"{e['fp_rate_pct']:.2f}% of {e['frames']} frames",
                              "reference": "0.00% of 4101 frames", "ok": e["fp_frames"] == 0 and e["frames"] == REFS["empty_frames"]})

    # ---- v6 on the partial 388 set: per-clip IoU 0.3 vs the v6 reference table ----
    if "v6|reserved388_partial" in out["scores"]:
        v = out["scores"]["v6|reserved388_partial"]["by_iou"]["0.3"]["per_clip_person"]
        for clip, (rate, n, fp) in REFS["v6_388_per_clip_iou0.3"].items():
            if clip not in v:
                out["checks"].append({"check": f"v6 reserved388 {clip} @IoU0.3", "measured": "NOT AVAILABLE (source clip missing)",
                                      "reference": f"{rate:.2f} of {n}", "ok": None})
                continue
            c = v[clip]
            ref_tp = round(rate * n)
            row = chk(f"v6 reserved388 {clip} @IoU0.3", c["tp"], c["n_gt"], ref_tp, n, rate_tol=0.02 + 0.005)
            row["reference"] = f"{rate:.2f} of {n} (~{ref_tp} boxes; FP {fp})"
            row["measured_fp"] = c["fp"]
            out["checks"].append(row)
        out["notes"].append("v6 388-set reference overall (0.577 @0.5 = 224/388, 0.585 @0.3 = 227/388) cannot be checked "
                            "directly: 4 of 11 source clips are not on disk. Only the per-clip rows above are checkable.")

    out["control_reproduced"] = all(c["ok"] for c in out["checks"] if c["check"].startswith("A ") and c["ok"] is not None)
    out["partial388_v6_reproduced"] = all(c["ok"] for c in out["checks"] if c["check"].startswith("v6 ") and c["ok"] is not None)
    if not out["control_reproduced"]:
        decision("CONTROL NOT REPRODUCED on at least one reference value (see raw/stage1_control.json 'checks'). "
                 "Both measured and reference values are reported; neither is treated as truth.")
    write_json(RAW / "stage1_control.json", out)

    # ---- ultralytics val of A on the fixed yaml (same procedure B/C get) ----
    try:
        log("S1 ultralytics val A on data_v7_fixed.yaml")
        mv = models["A_v7"].val(data=str(OUT / "data_v7_fixed.yaml"), imgsz=IMGSZ, batch=16, workers=0, split="val",
                                project=str(OUT / "runs"), name="A_v7_val", exist_ok=True, plots=False, verbose=False)
        out["A_val"] = {"mAP50": float(mv.box.map50), "mAP50_95": float(mv.box.map), "precision": float(mv.box.mp),
                        "recall": float(mv.box.mr)}
    except Exception as e:
        out["A_val"] = {"FAILED": repr(e), "tb": traceback.format_exc()[-2000:]}
    write_json(RAW / "stage1_control.json", out)
    log(f"S1 done. control_reproduced={out['control_reproduced']} partial388_v6={out['partial388_v6_reproduced']}")


if __name__ == "__main__":
    main()
