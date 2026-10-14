"""STAGE 0 -- preflight. Read-only on ROOT; writes only under OUT."""
import csv
import hashlib
import os
import shutil
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (OUT, RAW, ROOT, EVALSETS, WEIGHTS, PY, MODELS, log, write_json, decision,
                    import_by_path)

import cv2
import numpy as np
import yaml

R = {"stage": "S0_preflight"}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def env_info():
    import torch, ultralytics
    info = {"python": sys.version.split()[0], "executable": sys.executable,
            "torch": torch.__version__, "cuda": torch.cuda.is_available(),
            "ultralytics": ultralytics.__version__, "opencv": cv2.__version__}
    if torch.cuda.is_available():
        p = torch.cuda.get_device_properties(0)
        info.update(gpu=p.name, vram_gb=round(p.total_memory / 1e9, 2))
    try:
        import mediapipe
        info["mediapipe"] = mediapipe.__version__
    except Exception as e:
        info["mediapipe"] = f"import failed: {e}"
    # .venv status (tested in-session before launch; recorded here too)
    import subprocess
    r = subprocess.run([str(ROOT / ".venv" / "Scripts" / "python.exe"), "-c", "import torch"],
                       capture_output=True, text=True, timeout=120)
    info["venv_dot_venv"] = {"returncode": r.returncode, "stderr_tail": (r.stderr or "")[-300:]}
    return info


def weights_check():
    from ultralytics import YOLO
    out = {}
    for key in ("stock_yolo26n", "stock_yolov8n", "A_v7", "v6"):
        p = MODELS[key]
        m = YOLO(str(p))
        out[key] = {"path": str(p), "n_classes": len(m.names), "names0": m.names[0],
                    "sha256": sha256(p)}
    y = out["stock_yolo26n"]
    out["yolo26n_is_stock_80class"] = (y["n_classes"] == 80 and y["names0"] == "person")
    # yolo26s download (allowed); into OUT/weights only
    try:
        cwd = os.getcwd()
        os.chdir(WEIGHTS)
        try:
            m = YOLO("yolo26s.pt")
        finally:
            os.chdir(cwd)
        p = WEIGHTS / "yolo26s.pt"
        out["stock_yolo26s"] = {"path": str(p), "exists": p.exists(), "n_classes": len(m.names),
                                "names0": m.names[0], "sha256": sha256(p) if p.exists() else None}
    except Exception as e:
        out["stock_yolo26s"] = {"FAILED": repr(e), "tb": traceback.format_exc()[-1500:]}
        decision(f"yolo26s.pt download failed ({e!r}); stock_yolo26s is skipped everywhere.")
    out["stock_yolov8n_note"] = ("models/yolov8n.pt used as the stock yolov8n (80-class COCO, the "
                                 "same base A was trained from); not re-downloaded.")
    return out


def recipe_check():
    a1 = yaml.safe_load((ROOT / "runs/detect/v7_1epoch_benchmark2/args.yaml").read_text())
    full_dir = ROOT / "runs/detect/runs/detect/v7_full_train"
    a2 = yaml.safe_load((full_dir / "args.yaml").read_text()) if (full_dir / "args.yaml").exists() else None
    diffs = {}
    if a2:
        for k in sorted(set(a1) | set(a2)):
            if a1.get(k) != a2.get(k):
                diffs[k] = {"v7_1epoch_benchmark2": a1.get(k), "v7_full_train": a2.get(k)}
    rows = list(csv.DictReader(open(full_dir / "results.csv", encoding="utf-8")))
    rows = [{k.strip(): v for k, v in r.items()} for r in rows]
    ep = [int(float(r["epoch"])) for r in rows]
    t = [float(r["time"]) for r in rows]
    m50 = [float(r["metrics/mAP50(B)"]) for r in rows]
    m5095 = [float(r["metrics/mAP50-95(B)"]) for r in rows]
    per_epoch = [t[0]] + [t[i] - t[i - 1] for i in range(1, len(t))]
    best_i = int(np.argmax(m5095))
    fit = [0.1 * a + 0.9 * b for a, b in zip(m50, m5095)]
    best_fit_i = int(np.argmax(fit))
    return {
        "control_args_file": "runs/detect/v7_1epoch_benchmark2/args.yaml",
        "control_args": a1,
        "full_train_args_present": a2 is not None,
        "args_differences": diffs,
        "A_full_train": {
            "epochs_run": len(rows), "epochs_configured": (a2 or {}).get("epochs"),
            "patience": (a2 or {}).get("patience"),
            "best_epoch_by_mAP50_95": ep[best_i], "best_mAP50_95": m5095[best_i], "mAP50_at_that_epoch": m50[best_i],
            "best_epoch_by_fitness_0.1_0.9": ep[best_fit_i],
            "max_mAP50": max(m50), "final_epoch_mAP50": m50[-1], "final_epoch_mAP50_95": m5095[-1],
            "total_time_s": t[-1], "mean_s_per_epoch": t[-1] / len(rows),
            "median_s_per_epoch": float(np.median(per_epoch)), "per_epoch_s": per_epoch,
            "early_stopped": len(rows) < ((a2 or {}).get("epochs") or len(rows)),
        },
    }


def dataset_view():
    """data_v7_fixed.yaml. NOTE the path points at a junction view inside OUT, not at the dataset
    itself: Ultralytics writes labels/<split>.cache next to the label dirs, and the existing
    datasets/sage_merged_v7/labels/{train,val}.cache (Aug 22) would be REWRITTEN because their hash
    includes the old C:\\University paths. Junctions keep images/labels byte-identical while the
    cache lands in OUT."""
    import _winapi
    src = ROOT / "datasets" / "sage_merged_v7"
    orig = yaml.safe_load((src / "data.yaml").read_text())
    view = OUT / "dataset_view"
    for sub in ("images", "labels"):
        (view / sub).mkdir(parents=True, exist_ok=True)
        for split in ("train", "val"):
            link = view / sub / split
            if not link.exists():
                _winapi.CreateJunction(str(src / sub / split), str(link))
    fixed = dict(orig)
    fixed["path"] = str(view).replace("\\", "/")
    # A copy that literally points at the dataset path too, as the task text asked (not used for training).
    literal = dict(orig)
    literal["path"] = str(src).replace("\\", "/")
    (OUT / "data_v7_fixed.yaml").write_text(yaml.safe_dump(fixed, sort_keys=False), encoding="utf-8")
    (OUT / "data_v7_literal_path_NOT_USED.yaml").write_text(yaml.safe_dump(literal, sort_keys=False), encoding="utf-8")
    counts = {}
    for sub in ("images", "labels"):
        for split in ("train", "val"):
            d = view / sub / split
            counts[f"{sub}/{split}"] = sum(1 for _ in d.iterdir()) if d.is_dir() else None
    orig_counts = {f"{sub}/{split}": sum(1 for _ in (src / sub / split).iterdir())
                   for sub in ("images", "labels") for split in ("train", "val")}
    caches = {p.name: {"size": p.stat().st_size, "mtime": p.stat().st_mtime}
              for p in (src / "labels").glob("*.cache")}
    decision("Training/val use OUT/data_v7_fixed.yaml whose `path:` is OUT/dataset_view (NTFS junctions "
             "to datasets/sage_merged_v7/{images,labels}/{train,val}), not the dataset dir itself. Reason: "
             "Ultralytics would otherwise rewrite the existing labels/train.cache and val.cache (hash includes "
             "the pre-move paths), violating the read-only rule. Same files, same train/val split.")
    return {"orig_yaml": orig, "fixed_yaml": fixed, "view_counts": counts, "orig_counts": orig_counts,
            "orig_cache_files_before": caches, "train_val_unchanged": orig["train"] == fixed["train"] and orig["val"] == fixed["val"]}


# ---------------------------------------------------------------------------------------------
# Eval sets
# ---------------------------------------------------------------------------------------------

def count_boxes(labels_dir, cls=0, only=None):
    n = 0
    for p in Path(labels_dir).glob("*.txt"):
        if p.name == "classes.txt" or (only is not None and p.stem not in only):
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) >= 5 and int(float(parts[0])) == cls:
                n += 1
    return n


def build_eval_sets():
    sh = import_by_path("ov_sample_heldout", ROOT / "src/detection/sample_heldout_frames.py")
    rot = import_by_path("ov_footage_rotation", ROOT / "src/detection/footage_rotation.py")
    fp = import_by_path("ov_footage_paths", ROOT / "src/detection/footage_paths.py")
    src_set = ROOT / "eval" / "heldout_objects"
    src_imgs = sorted(p for p in (src_set / "images").iterdir() if p.suffix.lower() in {".jpg", ".png", ".jpeg"})
    label_stems = sorted(p.stem for p in (src_set / "labels").glob("*.txt") if p.name != "classes.txt")
    info = {"heldout_objects": {"images": len(src_imgs), "label_files": len(label_stems),
                                "person_boxes_with_image": count_boxes(src_set / "labels", 0, {p.stem for p in src_imgs}),
                                "person_boxes_all_labels": count_boxes(src_set / "labels", 0)}}

    # map clip key -> source video under Reserved/
    sources = {key: path for key, path in sh.iter_source_clips(fp.RESERVED_ROOT)}
    info["reserved_sources"] = {k: str(v) for k, v in sources.items()}

    def clip_of(stem):
        c, _, f = stem.rpartition("_")
        return (c, int(f)) if f.isdigit() else (stem, None)

    # orientation audit of the existing 200 images vs the registered rotation of their source
    audit = {}
    for p in src_imgs:
        clip, _ = clip_of(p.stem)
        if clip in audit:
            continue
        src = sources.get(clip)
        im = cv2.imread(str(p))
        entry = {"saved_hw": list(im.shape[:2]), "source": str(src) if src else None}
        if src is not None and not rot.needs_verification(src):
            r = rot.get_rotation(src)
            cap = cv2.VideoCapture(str(src))
            ok, fr = cap.read()
            cap.release()
            raw_hw = list(fr.shape[:2])
            rot_hw = list(rot.apply(fr, r).shape[:2])
            entry.update(registered_rotation=rot.describe(r), raw_hw=raw_hw, rotated_hw=rot_hw,
                         saved_matches_rotated=(entry["saved_hw"] == rot_hw),
                         saved_is_unrotated=(r is not None and entry["saved_hw"] == raw_hw and raw_hw != rot_hw))
        audit[clip] = entry
    info["orientation_audit"] = audit
    needs_rot = {c for c, e in audit.items() if e.get("saved_is_unrotated")}
    info["clips_saved_unrotated"] = sorted(needs_rot)

    # ---- set 1: heldout_objects_rotfix (same 200 frames, unrotated ones rotated with the registered rotation)
    d1 = EVALSETS / "heldout_objects_rotfix"
    (d1 / "images").mkdir(parents=True, exist_ok=True)
    (d1 / "labels").mkdir(parents=True, exist_ok=True)
    for p in src_imgs:
        clip, _ = clip_of(p.stem)
        dst = d1 / "images" / p.name
        if clip in needs_rot:
            if not dst.exists():
                im = cv2.imread(str(p))
                cv2.imwrite(str(dst), rot.apply(im, rot.get_rotation(sources[clip])))
        elif not dst.exists():
            shutil.copy2(p, dst)
        lab = src_set / "labels" / f"{p.stem}.txt"
        if lab.exists() and not (d1 / "labels" / lab.name).exists():
            shutil.copy2(lab, d1 / "labels" / lab.name)
    info["heldout_objects_rotfix"] = {"images": len(list((d1 / "images").iterdir())),
                                      "person_boxes": count_boxes(d1 / "labels", 0)}

    # ---- set 2: reserved388_partial. All labelled frames of the 388-box set whose image can be obtained:
    #   * frames already in eval/heldout_objects/images (rotation-fixed copy above)
    #   * frames re-extracted from the Reserved/ source video (sequential read, 1-based index, registered rotation)
    d2 = EVALSETS / "reserved388_partial"
    (d2 / "images").mkdir(parents=True, exist_ok=True)
    (d2 / "labels").mkdir(parents=True, exist_ok=True)
    by_clip = {}
    for stem in label_stems:
        clip, f = clip_of(stem)
        by_clip.setdefault(clip, []).append((f, stem))
    have = {p.stem for p in src_imgs}
    verify = []
    per_clip = {}
    for clip, frames in sorted(by_clip.items()):
        want = {f: s for f, s in frames}
        got = set()
        src = sources.get(clip)
        if src is not None and not rot.needs_verification(src) and clip.startswith("With_people"):
            r = rot.get_rotation(src)
            cap = cv2.VideoCapture(str(src))
            idx = 0
            maxf = max(want)
            while idx < maxf:
                ok, fr = cap.read()
                if not ok:
                    break
                idx += 1
                if idx in want:
                    img = rot.apply(fr, r)
                    stem = want[idx]
                    dst = d2 / "images" / f"{stem}.jpg"
                    cv2.imwrite(str(dst), img)
                    got.add(stem)
                    if stem in have:
                        ref = cv2.imread(str(d1 / "images" / f"{stem}.jpg"))
                        a = cv2.imread(str(dst))
                        if ref.shape == a.shape:
                            verify.append({"stem": stem, "mean_abs_diff": float(np.abs(ref.astype(int) - a.astype(int)).mean())})
                        else:
                            verify.append({"stem": stem, "shape_mismatch": [list(ref.shape), list(a.shape)]})
            cap.release()
        for f, stem in frames:
            if stem not in got and stem in have:
                shutil.copy2(d1 / "images" / f"{stem}.jpg", d2 / "images" / f"{stem}.jpg")
                got.add(stem)
        for stem in got:
            shutil.copy2(src_set / "labels" / f"{stem}.txt", d2 / "labels" / f"{stem}.txt")
        per_clip[clip] = {"labelled_frames": len(frames), "frames_available": len(got),
                          "person_boxes_labelled": count_boxes(src_set / "labels", 0, {s for _, s in frames}),
                          "person_boxes_available": count_boxes(src_set / "labels", 0, got),
                          "source": str(src) if src else None}
    diffs = [v["mean_abs_diff"] for v in verify if "mean_abs_diff" in v]
    info["reserved388_partial"] = {
        "per_clip": per_clip,
        "frames": sum(v["frames_available"] for v in per_clip.values()),
        "person_boxes": sum(v["person_boxes_available"] for v in per_clip.values()),
        "person_boxes_in_full_388_labels": sum(v["person_boxes_labelled"] for v in per_clip.values()),
        "clips_missing_source": sorted(c for c, v in per_clip.items() if v["frames_available"] < v["labelled_frames"]),
        "reextraction_check_vs_existing_images": {"n": len(diffs), "max_mean_abs_diff": max(diffs) if diffs else None,
                                                  "mean": float(np.mean(diffs)) if diffs else None,
                                                  "shape_mismatches": [v for v in verify if "shape_mismatch" in v]},
    }
    ok = bool(diffs) and max(diffs) < 4.0 and not info["reserved388_partial"]["reextraction_check_vs_existing_images"]["shape_mismatches"]
    info["reserved388_partial"]["extraction_verified"] = ok
    if not ok:
        decision("reserved388_partial re-extraction did NOT match the existing images closely (see raw/preflight.json); "
                 "the set is still scored but flagged UNVERIFIED.")

    r6 = ROOT / "handlabels" / "round6_heldout"
    info["round6_heldout"] = {"images": len(list((r6 / "images").iterdir())),
                              "label_files": len([p for p in (r6 / "labels").glob("*.txt") if p.name != "classes.txt"]),
                              "person_boxes": count_boxes(r6 / "labels", 0)}
    # empty-room set
    empty = fp.RESERVED_EMPTY
    clips = sorted(p for p in empty.rglob("*") if p.suffix.lower() in {".mp4", ".mov", ".avi", ".mkv"})
    info["reserved_empty"] = {"dir": str(empty), "clips": [p.name for p in clips],
                              "frame_count_metadata": {p.name: int(cv2.VideoCapture(str(p)).get(cv2.CAP_PROP_FRAME_COUNT)) for p in clips}}
    info["reserved_empty"]["frame_count_metadata_total"] = sum(info["reserved_empty"]["frame_count_metadata"].values())
    return info


def luma_thresholds():
    """Pre-registered dark/bright definition, computed from pixels only, before any enhancement result."""
    from score_lib import EVAL_SETS, list_images
    out = {"definition": "mean Y of YCrCb per frame; dark = luma <= 33.333rd percentile of that eval set's "
                         "labelled frames, bright = luma >= 66.667th percentile (numpy linear percentile)",
           "sets": {}}
    for name, d in EVAL_SETS.items():
        imgs = list_images(name)
        lum = {}
        for p in imgs:
            im = cv2.imread(str(p))
            lum[p.name] = float(cv2.cvtColor(im, cv2.COLOR_BGR2YCrCb)[:, :, 0].mean())
        v = np.array(list(lum.values()))
        lo, hi = float(np.percentile(v, 100 / 3)), float(np.percentile(v, 200 / 3))
        out["sets"][name] = {"dark_max_luma": lo, "bright_min_luma": hi, "n_frames": len(v),
                             "n_dark": int((v <= lo).sum()), "n_bright": int((v >= hi).sum()), "luma": lum}
    return out


def main():
    steps = [("env", env_info), ("weights", weights_check), ("recipe", recipe_check),
             ("dataset", dataset_view), ("evalsets", build_eval_sets), ("luma", luma_thresholds)]
    for name, fn in steps:
        log(f"preflight: {name}")
        try:
            R[name] = fn()
        except Exception as e:
            R[name] = {"FAILED": repr(e), "traceback_tail": traceback.format_exc()[-3000:]}
            log(f"preflight {name} FAILED: {e!r}")
        write_json(RAW / "preflight.json", R)
    lum = R.get("luma", {})
    if "sets" in lum:
        write_json(RAW / "luma_thresholds.json", lum)
    failed = [k for k, v in R.items() if isinstance(v, dict) and "FAILED" in v and k not in ("weights",)]
    log(f"preflight done; failed steps: {failed}")
    if any(k in failed for k in ("env", "dataset", "evalsets")):
        sys.exit(2)


if __name__ == "__main__":
    main()
