"""Compare v7 with the cross-clip fine-tune on data neither model trained on.

Sets (both unseen by both models):
  - Laying_Dim_HM (153 dark frames), corrected labels (round6_heldout_v2, PROVISIONAL) and original labels
  - eval/heldout_objects (200 frames, general), to check nothing regressed
Scoring is src/detection/score_v7_suite.score_model, unchanged (conf 0.4, imgsz 640, same-class
greedy matching by confidence), at IoU 0.5 and 0.3. Writes compare_ft.md next to this file.

usage: python compare_ft.py [path/to/finetuned.pt]
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
import src.detection.score_v7_suite as suite  # noqa: E402
from src.detection.score_heldout_objects import load_ground_truth  # noqa: E402
from ultralytics import YOLO  # noqa: E402

FT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "runs" / "ft_behindbed" / "weights" / "best.pt"
MODELS = {"v7 (current)": REPO / "models" / "yolov8n_sage_merged_v7.pt", "v7 + Behind_Bed fine-tune": FT}
TEST_CLIP = "Laying_Dim_HM"


def subset(eval_dir, clip=None):
    imgs = sorted(p for p in (eval_dir / "images").iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    if clip:
        imgs = [p for p in imgs if p.name.startswith(clip + "_")]
    gt, unl = load_ground_truth(eval_dir / "labels", imgs)
    return gt, unl


SETS = {
    "Laying_Dim_HM (dark, unseen), corrected labels [PROVISIONAL]": subset(REPO / "handlabels" / "round6_heldout_v2", TEST_CLIP),
    "Laying_Dim_HM (dark, unseen), original labels": subset(REPO / "handlabels" / "round6_heldout", TEST_CLIP),
    "eval/heldout_objects (general, unseen)": subset(REPO / "eval" / "heldout_objects"),
}

models = {}
for name, path in MODELS.items():
    if not path.exists():
        sys.exit(f"STOP: {name} weights not found at {path}")
    models[name] = YOLO(str(path))

lines = ["# v7 vs v7 + Behind_Bed_HM fine-tune, on frames neither model trained on", "",
         "PROVISIONAL: the corrected labels are not yet verified. Fine-tune: v7 weights + 5 epochs on",
         "v7's training data plus the 145 corrected Behind_Bed_HM frames (see train_ft.py).", ""]
for thr in (0.5, 0.3):
    lines += [f"## IoU {thr}", ""]
    for sname, (gt, unl) in SETS.items():
        n_boxes = sum(len(v) for v in gt.values())
        lines += [f"### {sname}", "", f"{len(gt)} frames, {n_boxes} labelled boxes ({len(unl)} unlabelled, excluded)", ""]
        stats = {m: suite.score_model(model, gt, thr)[0] for m, model in models.items()}
        lines.append("| class | n |" + "".join(f" {m} P | {m} R |" for m in models))
        lines.append("|---|---|" + "---|---|" * len(models))
        for idx, cls in enumerate(suite.SAGE_CLASSES):
            n = sum(1 for b in gt.values() for x in b if x[0] == idx)
            if not n:
                continue
            row = f"| {cls} | {n} |"
            for m in models:
                s = stats[m].get(idx, {"tp": 0, "fp": 0, "fn": 0})
                tp, fp, fn = s["tp"], s["fp"], s["fn"]
                p = f"{tp / (tp + fp):.2f}" if tp + fp else "n/a"
                r = f"{tp / (tp + fn):.2f}" if tp + fn else "n/a"
                row += f" {p} | {r} ({tp}/{tp + fn}, fp {fp}) |"
            lines.append(row)
            print(sname, thr, row, flush=True)
        lines.append("")
(HERE / "compare_ft.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("Wrote", HERE / "compare_ft.md")
