"""Overlay A (v7) and A2 training curves from their Ultralytics results.csv files. Read-only on inputs.
Writes benchmarks/phase3_a2/A_vs_A2_training_curves.png."""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
OUT = ROOT / "benchmarks" / "phase3_a2"
RUNS = {"A (v7)": ROOT / "runs" / "detect" / "runs" / "detect" / "v7_full_train" / "results.csv",
        "A2": OUT / "runs" / "A2" / "results.csv"}
COLORS = {"A (v7)": "#2a78d6", "A2": "#eb6834"}
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
PANELS = [("train/box_loss", "Train box loss"), ("train/cls_loss", "Train class loss"),
          ("metrics/mAP50(B)", "Val mAP50 (all 13 classes)"), ("val/box_loss", "Val box loss"),
          ("val/cls_loss", "Val class loss"), ("metrics/mAP50-95(B)", "Val mAP50-95 (all 13 classes)")]


def load(p):
    rows = [{k.strip(): float(v) for k, v in r.items()} for r in csv.DictReader(open(p, encoding="utf-8"))]
    return rows


data = {k: load(p) for k, p in RUNS.items()}

# Check that the v7 log belongs to model A's checkpoint (same final metrics).
ck = torch.load(ROOT / "models" / "yolov8n_sage_merged_v7.pt", weights_only=False, map_location="cpu")
tm = ck.get("train_metrics") or {}
ck_map = tm.get("metrics/mAP50-95(B)")
log_best = max(r["metrics/mAP50-95(B)"] for r in data["A (v7)"])
print(f"ckpt train_metrics mAP50-95={ck_map}  v7 log best mAP50-95={log_best:.5f}  train_args.name={ck['train_args'].get('name')}")

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK})
fig, axes = plt.subplots(2, 3, figsize=(12, 6.6), facecolor=SURFACE)
for ax, (col, title) in zip(axes.flat, PANELS):
    ax.set_facecolor(SURFACE)
    ends = []
    for name, rows in data.items():
        ep = [r["epoch"] for r in rows]
        ys = [r[col] for r in rows]
        ax.plot(ep, ys, color=COLORS[name], lw=2, solid_capstyle="round", label=name)
        ends.append((ys[-1], name, ep[-1]))
    # end labels: keep at least 7% of the y-range apart so close finishes stay readable
    lo, hi = ax.get_ylim()
    gap = 0.07 * (hi - lo)
    ends.sort()
    (y0, n0, x0), (y1, n1, x1) = ends
    mid = (y0 + y1) / 2
    ly0, ly1 = (min(y0, mid - gap / 2), max(y1, mid + gap / 2)) if y1 - y0 < gap else (y0, y1)
    for (y, n, x), ly in ((ends[0], ly0), (ends[1], ly1)):
        ax.annotate(f"{n} {y:.3f}", (x, y), xytext=(x + 0.6, ly), textcoords="data", va="center", fontsize=8, color=INK2)
    ax.axvline(20.5, color=INK2, lw=0.8, ls=(0, (3, 3)), alpha=0.6)
    ax.set_title(title, loc="left", fontsize=10, color=INK, pad=6)
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_xlim(0.5, 34)
    ax.set_xlabel("epoch")
axes[0, 0].text(20.8, axes[0, 0].get_ylim()[1], "mosaic off\n(last 10 epochs)", fontsize=7, color=INK2, va="top")
handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper right", ncol=2, frameon=False, bbox_to_anchor=(0.985, 0.985))
fig.suptitle("Training curves: A (v7) vs A2", x=0.012, ha="left", fontsize=13, fontweight="bold", y=0.985)
fig.text(0.012, 0.935, "Same recipe, seed and validation split (2,610 images). A2's training set drops 2,450 auto-labelled frames "
         "from two dim clips (12,593 vs 15,043 images).", fontsize=9, color=INK2)
fig.text(0.012, 0.012, "Val curves are directly comparable (identical val set). Train losses are measured on different training sets. "
         "Source: Ultralytics results.csv for each run.", fontsize=7.5, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 0.92))
out = OUT / "A_vs_A2_training_curves.png"
fig.savefig(out, dpi=160, facecolor=SURFACE)
print("wrote", out)
sys.exit(0)
