"""Overlay A (v7, 30 ep), A2 (30 ep, filtered data) and A50 (50 ep) training curves from their
Ultralytics results.csv files. Read-only on inputs. Writes benchmarks/phase4_a50/A_A2_A50_training_curves.png."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
OUT = ROOT / "benchmarks" / "phase4_a50"
RUNS = {"A (30 ep)": ROOT / "runs" / "detect" / "runs" / "detect" / "v7_full_train" / "results.csv",
        "A2 (30 ep, filtered)": ROOT / "benchmarks" / "phase3_a2" / "runs" / "A2" / "results.csv",
        "A50 (50 ep)": OUT / "runs" / "A50" / "results.csv"}
COLORS = {"A (30 ep)": "#2a78d6", "A2 (30 ep, filtered)": "#eb6834", "A50 (50 ep)": "#1baf7a"}
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
PANELS = [("train/box_loss", "Train box loss"), ("train/cls_loss", "Train class loss"),
          ("metrics/mAP50(B)", "Val mAP50 (all 13 classes)"), ("val/box_loss", "Val box loss"),
          ("val/cls_loss", "Val class loss"), ("metrics/mAP50-95(B)", "Val mAP50-95 (all 13 classes)")]
SHORT = {"A (30 ep)": "A", "A2 (30 ep, filtered)": "A2", "A50 (50 ep)": "A50"}

data = {k: [{kk.strip(): float(v) for kk, v in r.items()} for r in csv.DictReader(open(p, encoding="utf-8"))]
        for k, p in RUNS.items()}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK})
fig, axes = plt.subplots(2, 3, figsize=(13, 6.8), facecolor=SURFACE)
for ax, (col, title) in zip(axes.flat, PANELS):
    ax.set_facecolor(SURFACE)
    ends = []
    for name, rows in data.items():
        ep = [r["epoch"] for r in rows]
        ys = [r[col] for r in rows]
        ax.plot(ep, ys, color=COLORS[name], lw=2, solid_capstyle="round", label=name)
        ends.append([ys[-1], name, ep[-1]])
    ax.axvline(20.5, color=COLORS["A (30 ep)"], lw=0.8, ls=(0, (3, 3)), alpha=0.5)
    ax.axvline(40.5, color=COLORS["A50 (50 ep)"], lw=0.8, ls=(0, (3, 3)), alpha=0.6)
    lo, hi = ax.get_ylim()
    gap = 0.075 * (hi - lo)
    # end labels: one per run at its last epoch, nudged apart vertically when they would overlap
    for x in sorted({e[2] for e in ends}):
        grp = sorted([e for e in ends if e[2] == x])
        pos = [g[0] for g in grp]
        for i in range(1, len(pos)):
            if pos[i] - pos[i - 1] < gap:
                pos[i] = pos[i - 1] + gap
        overflow = pos[-1] - (hi - 0.6 * gap)  # keep the stack inside the plot, below the panel title
        if overflow > 0:
            pos = [p - overflow for p in pos]
        for g, ly in zip(grp, pos):
            ax.annotate(f"{SHORT[g[1]]} {g[0]:.3f}", (x, g[0]), xytext=(x + 0.8, ly), textcoords="data",
                        va="center", fontsize=8, color=INK2)
    ax.set_title(title, loc="left", fontsize=10, color=INK, pad=6)
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_xlim(0.5, 58)
    ax.set_xlabel("epoch")
handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper right", ncol=3, frameon=False, bbox_to_anchor=(0.99, 0.985))
fig.suptitle("Training curves: A vs A2 vs A50", x=0.012, ha="left", fontsize=13, fontweight="bold", y=0.985)
fig.text(0.012, 0.935, "Same recipe, seed, optimizer (AdamW, lr 0.000588) and validation split (2,610 images). "
         "A50 = A trained for 50 epochs; A2 = A minus 2,450 auto-labelled dim frames.", fontsize=9, color=INK2)
fig.text(0.012, 0.012, "Dashed lines: mosaic augmentation switched off for the last 10 epochs (blue: A and A2 at epoch 21; aqua: A50 at epoch 41). "
         "Val curves are directly comparable; train losses for A2 come from a different training set.", fontsize=7.5, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 0.92))
out = OUT / "A_A2_A50_training_curves.png"
fig.savefig(out, dpi=160, facecolor=SURFACE)
print("wrote", out)
