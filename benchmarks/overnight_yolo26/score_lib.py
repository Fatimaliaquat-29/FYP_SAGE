"""Scoring harness. REUSES `iou` and `load_ground_truth` from src/detection/score_heldout_objects.py
(imported by path, not copied) and the empty-room `score_clip` from score_empty_false_positives.py.

Matching mirrors score_heldout_objects.score_loaded_model exactly: predictions sorted by confidence,
each claims the highest-IoU unmatched GT box OF THE SAME CLASS, TP iff that IoU >= threshold, else FP;
unmatched GT boxes are FN. Predictions are cached once per (model, set, conf, enhancement) so both IoU
thresholds, per-clip and dark/bright breakdowns come from the same inference pass.

Stock COCO models: only COCO class 0 is kept and mapped to SAGE person; ground truth is filtered to
person (only_classes={0} on both sides, exactly what --classes person does in the original script).
"""
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, RAW, EVALSETS, CONF, IMGSZ, STOCK, import_by_path, read_json, write_json, wilson

import cv2
import numpy as np

_sho = import_by_path("ov_score_heldout_objects", ROOT / "src/detection/score_heldout_objects.py")
iou = _sho.iou
load_ground_truth = _sho.load_ground_truth
score_loaded_model = _sho.score_loaded_model          # used only for the harness-equality cross-check
group_by_clip = _sho.group_by_clip
SAGE_CLASSES = import_by_path("ov_sage_classes", ROOT / "src/detection/sage_classes.py").SAGE_CLASSES

EVAL_SETS = {
    "heldout_objects": ROOT / "eval" / "heldout_objects",
    "heldout_objects_rotfix": EVALSETS / "heldout_objects_rotfix",
    "reserved388_partial": EVALSETS / "reserved388_partial",
    "round6_heldout": ROOT / "handlabels" / "round6_heldout",
}
EVAL_SET_DESC = {
    "heldout_objects": "eval/heldout_objects as stored (200 frames; 93 person boxes; Bedroom_Fall frames stored UNROTATED)",
    "heldout_objects_rotfix": "same 200 frames/labels, Bedroom_Fall frames rotated with the registered rotation (copy in OUT)",
    "reserved388_partial": "the 388-box reserved posture labels, restricted to frames whose image exists or could be "
                           "re-extracted from yolo_testing/Reserved (7 of 11 clips' sources exist)",
    "round6_heldout": "handlabels/round6_heldout (Laying_Dim_HM + Behind_Bed_HM; 226 person boxes)",
}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp"}
PRED_DIR = RAW / "preds"
PRED_DIR.mkdir(parents=True, exist_ok=True)


def list_images(set_name):
    d = EVAL_SETS[set_name] / "images"
    return sorted(p for p in d.iterdir() if p.suffix.lower() in IMAGE_EXT)


def load_set(set_name):
    imgs = list_images(set_name)
    gt, unlabelled = load_ground_truth(EVAL_SETS[set_name] / "labels", imgs)
    return gt, unlabelled


def clip_of(name):
    stem = Path(name).stem
    c, _, f = stem.rpartition("_")
    return c if c and f.isdigit() else stem


# ---------------------------------------------------------------------------------------------
# Enhancement (Stage 3)
# ---------------------------------------------------------------------------------------------
_CLAHE = None


def _gamma(img, g):
    lut = np.array([((i / 255.0) ** g) * 255.0 for i in range(256)]).clip(0, 255).astype(np.uint8)
    return cv2.LUT(img, lut)


def _clahe(img):
    global _CLAHE
    if _CLAHE is None:
        _CLAHE = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    return cv2.cvtColor(cv2.merge((_CLAHE.apply(l), a, b)), cv2.COLOR_LAB2BGR)


ENHANCEMENTS = {
    "none": None,
    "gamma0.6": lambda im: _gamma(im, 0.6),
    "gamma0.5": lambda im: _gamma(im, 0.5),
    "clahe": _clahe,
    "gamma0.6+clahe": lambda im: _clahe(_gamma(im, 0.6)),
}


# ---------------------------------------------------------------------------------------------
# Prediction (cached)
# ---------------------------------------------------------------------------------------------

def predict_set(model, model_key, set_name, conf=CONF, imgsz=IMGSZ, enhancement="none", force=False):
    """Returns {image_name: [[conf, sage_cls, [x1,y1,x2,y2] normalised], ...]} (cached JSON)."""
    cache = PRED_DIR / f"{model_key}__{set_name}__c{conf}__{enhancement}.json"
    if cache.exists() and not force:
        return read_json(cache)
    fn = ENHANCEMENTS[enhancement]
    stock = model_key in STOCK
    out = {}
    for p in list_images(set_name):
        src = str(p) if fn is None else fn(cv2.imread(str(p)))
        preds = []
        for r in model.predict(src, conf=conf, imgsz=imgsz, verbose=False):
            for box in r.boxes:
                c = int(box.cls.item())
                if stock:
                    if c != 0:
                        continue      # stock COCO: only class 0 (person) is scored
                preds.append([float(box.conf.item()), c, [float(v) for v in box.xyxyn[0]]])
        preds.sort(key=lambda x: -x[0])
        out[p.name] = preds
    write_json(cache, out)
    return out


# ---------------------------------------------------------------------------------------------
# Matching (identical logic to score_loaded_model)
# ---------------------------------------------------------------------------------------------

def match_image(gt_boxes, preds, iou_thr, only_classes=None):
    """gt_boxes: [(cls,x1,y1,x2,y2)], preds: [[conf,cls,[box]]] sorted by -conf.
    Returns {cls: [tp, fp, fn]}."""
    stats = defaultdict(lambda: [0, 0, 0])
    gts = [g for g in gt_boxes if only_classes is None or g[0] in only_classes]
    unmatched = list(range(len(gts)))
    for _, cls, box in preds:
        if only_classes is not None and cls not in only_classes:
            continue
        best, bi = 0.0, None
        for gi in unmatched:
            gcls, *gbox = gts[gi]
            if gcls != cls:
                continue
            o = iou(tuple(box), tuple(gbox))
            if o > best:
                best, bi = o, gi
        if bi is not None and best >= iou_thr:
            stats[cls][0] += 1
            unmatched.remove(bi)
        else:
            stats[cls][1] += 1
    for gi in unmatched:
        stats[gts[gi][0]][2] += 1
    return stats


def score_preds(gt, preds, iou_thr, stock=False, subset=None):
    """Per-image stats -> aggregate. subset: optional set of image names to restrict to.
    Returns dict with per_class totals, person totals, per_clip person totals."""
    only = {0} if stock else None
    per_class = defaultdict(lambda: [0, 0, 0])
    per_clip = defaultdict(lambda: [0, 0, 0])
    for path, boxes in gt.items():
        name = Path(path).name
        if subset is not None and name not in subset:
            continue
        st = match_image(boxes, preds.get(name, []), iou_thr, only)
        for c, v in st.items():
            for i in range(3):
                per_class[c][i] += v[i]
        pv = st.get(0, [0, 0, 0])
        for i in range(3):
            per_clip[clip_of(name)][i] += pv[i]
    return {"per_class": {int(c): v for c, v in per_class.items()},
            "person": list(per_class.get(0, [0, 0, 0])),
            "per_clip_person": dict(per_clip)}


def summarise(tp, fp, fn):
    n = tp + fn
    r = tp / n if n else None
    p = tp / (tp + fp) if tp + fp else None
    lo, hi = wilson(tp, n)
    return {"tp": tp, "fp": fp, "fn": fn, "n_gt": n, "recall": r, "precision": p,
            "recall_wilson95": [lo, hi]}


def score_model_on_set(model, model_key, set_name, conf=CONF, enhancement="none"):
    gt, unl = load_set(set_name)
    preds = predict_set(model, model_key, set_name, conf=conf, enhancement=enhancement)
    stock = model_key in STOCK
    res = {"model": model_key, "set": set_name, "conf": conf, "imgsz": IMGSZ, "enhancement": enhancement,
           "n_frames": len(gt), "n_unlabelled_excluded": len(unl), "by_iou": {}}
    for thr in (0.5, 0.3):
        s = score_preds(gt, preds, thr, stock)
        res["by_iou"][str(thr)] = {
            "person": summarise(*s["person"]),
            "per_clip_person": {c: summarise(*v) for c, v in sorted(s["per_clip_person"].items())},
            "per_class": ({} if stock else {SAGE_CLASSES[c] if c < len(SAGE_CLASSES) else f"cls{c}": summarise(*v)
                                             for c, v in sorted(s["per_class"].items())}),
        }
    return res


# ---------------------------------------------------------------------------------------------
# Empty-room FP (imports the project's own score_clip)
# ---------------------------------------------------------------------------------------------

def empty_room_fp(model, model_key, conf=CONF, imgsz=IMGSZ):
    cache = RAW / "empty_fp" / f"{model_key}__c{conf}.json"
    if cache.exists():
        return read_json(cache)
    sef = import_by_path("ov_score_empty_fp", ROOT / "src/detection/score_empty_false_positives.py")
    fpaths = import_by_path("ov_footage_paths2", ROOT / "src/detection/footage_paths.py")
    empty_dir = fpaths.RESERVED_EMPTY
    clips = sorted(p for p in empty_dir.rglob("*") if p.suffix.lower() in sef.VIDEO_EXTENSIONS | sef.IMAGE_EXTENSIONS)
    out = {"model": model_key, "conf": conf, "imgsz": imgsz, "stride": 1, "dir": str(empty_dir), "clips": {}}
    tf = tfp = tb = 0
    for c in clips:
        n, fpf, boxes, other, worst = sef.score_clip(model, c, 1, conf, imgsz)
        out["clips"][c.name] = {"frames": n, "fp_frames": fpf, "person_boxes": boxes, "worst": worst}
        tf += n
        tfp += fpf
        tb += boxes
    out.update(frames=tf, fp_frames=tfp, person_boxes=tb, fp_rate_pct=100.0 * tfp / tf if tf else None)
    write_json(cache, out)
    return out
