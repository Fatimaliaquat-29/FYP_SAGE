"""Builds AUDIT.md from files this audit wrote (raw/audit_stats.json, train_images.csv, audit_sheet.csv,
raw/sample_meta.json, raw/bedding_signature.json, READING.md). Writes raw/ai_tally.json and look_first.csv."""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
R = json.load(open(OUT / "raw/audit_stats.json"))
sheet = list(csv.DictReader(open(OUT / "audit_sheet.csv", encoding="utf-8")))
meta = json.load(open(OUT / "raw/sample_meta.json"))
imgs = {r["filename"]: r for r in csv.DictReader(open(OUT / "train_images.csv", encoding="utf-8"))}
sig = json.load(open(OUT / "raw/bedding_signature.json"))
L = []
P = L.append
V = ["OK", "BAD_BOX", "MISSING_PERSON_BOX", "UNCLEAR"]


def pct(a, b):
    return f"{a}/{b} ({100 * a / b:.1f}%)" if b else "--"


P("# Training-label audit -- datasets/sage_merged_v7 (train split)")
P("")
P(f"Generated from files in benchmarks/label_audit/ (stats run {R['generated']}). Read-only on the dataset: images and label "
  "files were read directly; no ultralytics train/val, no data.yaml loading by ultralytics. Dataset label caches unchanged "
  "(raw/raw_cache_before.txt vs the post-run listing in DECISIONS.md).")
P("")
P("**Two kinds of evidence, never mixed:** (1) automatic flags from a stock detector -- leads, not verdicts; (2) a provisional "
  "reading of 120 sampled images by an AI (Claude) -- **UNVERIFIED, not ground truth**; the human columns in audit_sheet.csv are empty.")
P("")
cc = R["class_check"]
P(f"Class order: src/detection/sage_classes.py vs datasets/sage_merged_v7/data.yaml names -> **{'identical' if cc['match'] else 'MISMATCH'}** "
  f"({len(cc['sage_classes'])} classes, person = index {cc['sage_classes'].index('person')}).")
P("")

# (a) inventory
inv = R["inventory"]
P("## (a) Inventory")
P("")
P(f"- images {inv['images']}, label files {inv['label_files']}, images without a label file {inv['images_without_label_file']}, "
  f"images with an empty label file {inv['images_with_empty_label_file']}, label files without an image {inv['label_files_without_image']}, "
  f"boxes with out-of-schema class ids {inv['out_of_schema_class_boxes'] or 0}.")
d = R["duplicates"]
P(f"- `_rN` repeat copies (build_merged_dataset --own_repeat): {d['repeat_copies']}, of which md5-identical to their original: "
  f"{d['repeat_copies_md5_identical_to_original']}. Other md5 duplicates (not explained by `_rN`): {d['files_in_duplicate_groups_that_are_not_rN_copies']} files.")
# who are the non-rN duplicates?
by = defaultdict(list)
for f, r in imgs.items():
    by[r["md5"]].append(r)
pairs = Counter()
for g in by.values():
    base = [r for r in g if r["repeat"] == "0"]
    if len(base) > 1:
        pairs[" == ".join(sorted({r["clip"] for r in base}))] += len(base) - 1
if pairs:
    P("  Non-repeat duplicate groups by clip (identical frames under different names): " +
      "; ".join(f"`{k}` x{v}" for k, v in pairs.most_common(10)) + ".")
P("")
P("| source (filename prefix) | images | of which `_rN` copies | person boxes | mean person boxes / image | images with 0 person boxes |")
P("|---|---|---|---|---|---|")
note = {"coco": "COCO (external dataset; name is explicit)", "own": "own footage", "empty": "own empty-room footage"}
for k, v in R["by_top"].items():
    P(f"| `{k}_` -- {note.get(k, '')} | {v['images']} | {v['repeat_copies']} | {v['person_boxes']} | {v['mean_person_per_image']:.2f} | {pct(v['zero_person'], v['images'])} |")
P("")
P("Person-label provenance (from handlabels/ cross-check; see DECISIONS.md):")
P("")
P("| provenance | images | person boxes | mean / image | 0-person images |")
P("|---|---|---|---|---|")
for k, v in R["by_provenance"].items():
    P(f"| {k} | {v['images']} | {v['person_boxes']} | {v['mean_person_per_image']:.2f} | {pct(v['zero_person'], v['images'])} |")
P("")
P("<details><summary>Per clip</summary>")
P("")
P("| clip | images | person boxes | mean / image | 0-person images |")
P("|---|---|---|---|---|")
for k, v in R["by_clip"].items():
    P(f"| {k} | {v['images']} | {v['person_boxes']} | {v['mean_person_per_image']:.2f} | {pct(v['zero_person'], v['images'])} |")
P("")
P("</details>")
P("")
dk = R["darkness"]
P(f"Darkness: mean luma per image in train_images.csv; dark = luma <= {dk['dark_max_luma']:.1f} (bottom third of ALL train images), "
  f"bright = luma >= {dk['bright_min_luma']:.1f}. Distribution by source: " +
  "; ".join(f"{t}: " + ", ".join(f"{b} {n}" for b, n in sorted(c.items())) for t, c in dk["by_top_bucket"].items()) + ".")
P("")

# (b) leakage
P("## (b) Leakage check")
P("")
P("| eval set | eval images | filename overlap | overlap after stripping `own_`/`coco_`/`empty_` and `_rN` | md5 overlap |")
P("|---|---|---|---|---|")
for k, v in R["leakage"].items():
    P(f"| {k} | {v['eval_images']} | {v['filename_overlap']} | {v['filename_overlap_after_stripping_source_prefix']} | {v['md5_overlap']} |")
P("")
tv = json.load(open(OUT / "raw/train_val_md5_overlap.json"))
P(f"Train vs val split of the same dataset: {tv['val_images_md5_identical_to_a_train_image']} of {tv['val_images']} val images are md5-identical to a train image.")
P("")
P("md5 catches byte-identical copies only; a re-encoded or re-extracted frame of the same video moment would not match.")
P("")

# (c) auto flags
s = R["auto_flags_setup"]
P("## (c) Automatic flags (detector proxy -- leads, NOT verdicts)")
P("")
P(f"Detector `{Path(s['detector']).name}` (stock COCO, person class only), imgsz {s['imgsz']}, run on {s['n_checked']} images "
  f"(stride {s['stride']}): {s['population']}. **SUSPECTED_MISSING** = a detection with conf >= {s['conf_detect']} whose best IoU "
  f"with every GT person box is < {s['iou_threshold']}. **SUSPECTED_PHANTOM** = a GT person box with no detection (conf >= "
  f"{s['conf_phantom_support']}) at IoU >= {s['iou_threshold']}. The detector itself fails on dark, occluded and lying people "
  "and fires on reflections/posters, so a flag says 'detector and label disagree', not which one is wrong. Calibration point: on "
  "frames whose person boxes were HAND-drawn, the detector disagrees with the label (PHANTOM) at the rates shown below; that is "
  "mostly the detector's own miss rate on hard footage.")
P("")
for title, key in (("by provenance", "flags_by_provenance"), ("by darkness bucket", "flags_by_dark_bucket"),
                   ("by provenance x darkness", "flags_by_provenance_x_dark"),
                   ("by lying proxy (GT person box wider than tall in pixels -- crude)", "flags_by_lying_proxy"),
                   ("by source prefix", "flags_by_top")):
    P(f"**{title}**")
    P("")
    P("| group | images checked | with SUSPECTED_MISSING | with SUSPECTED_PHANTOM | phantom GT boxes / GT person boxes |")
    P("|---|---|---|---|---|")
    for k, e in R[key].items():
        P(f"| {k} | {e['checked']} | {pct(e['with_missing'], e['checked'])} | {pct(e['with_phantom'], e['checked'])} | {e['phantom_boxes']}/{e['gt_person_boxes']} |")
    P("")
P("<details><summary>by clip</summary>")
P("")
P("| clip | images checked | with SUSPECTED_MISSING | with SUSPECTED_PHANTOM |")
P("|---|---|---|---|")
for k, e in R["flags_by_clip"].items():
    P(f"| {k} | {e['checked']} | {pct(e['with_missing'], e['checked'])} | {pct(e['with_phantom'], e['checked'])} |")
P("")
P("</details>")
P("")

# (d) AI tally
P("## (d) Provisional AI review of 120 sampled images -- UNVERIFIED")
P("")
sm = R["sample"]
P(f"Sample (seed {sm['seed']}): 40 uniform random + 40 SUSPECTED_MISSING + 20 SUSPECTED_PHANTOM + 20 from the darkest 10% of own "
  f"footage (luma <= {sm['darkest_10pct_own_luma_cut']:.1f}), deduplicated, shortfalls {sm['short_filled']}. Contact sheets: "
  "sheets/sheet_NN.jpg, sheet n = idx 9(n-1)+1..9n row-major; GREEN = GT person box, RED = detector box (conf>=0.5) matching no GT "
  "person, thin GREY = other GT classes; darkest tiles are display-brightened (labelled on the tile). Verdicts are Claude's "
  "reading of those sheets at contact-sheet resolution; **a human has not checked them.**")
P("")
tally = {}
for key, fn in (("sampling_reason", lambda r: r["sampling_reason"]), ("source (clip)", lambda r: r["source"]),
                ("provenance", lambda r: meta[r["filename"]]["provenance"]),
                ("darkness bucket", lambda r: meta[r["filename"]]["dark_bucket"])):
    g = defaultdict(Counter)
    for r in sheet:
        g[fn(r)][r["verdict_ai"]] += 1
        g["ALL"][r["verdict_ai"]] += 1
    tally[key] = {k: dict(v) for k, v in g.items()}
    P(f"**AI verdicts by {key}**")
    P("")
    P("| group | n | " + " | ".join(V) + " |")
    P("|---|---|" + "---|" * len(V))
    for k, c in sorted(g.items(), key=lambda x: (x[0] == "ALL", x[0])):
        n = sum(c.values())
        P(f"| {k} | {n} | " + " | ".join(pct(c.get(x, 0), n) for x in V) + " |")
    P("")
json.dump(tally, open(OUT / "raw/ai_tally.json", "w"), indent=1)
rnd = [r for r in sheet if r["sampling_reason"] == "random"]
P(f"Only the 40 'random' rows estimate a rate for the whole checked population: AI BAD_BOX {pct(sum(r['verdict_ai'] == 'BAD_BOX' for r in rnd), len(rnd))}, "
  f"UNCLEAR {pct(sum(r['verdict_ai'] == 'UNCLEAR' for r in rnd), len(rnd))}. The other rows were chosen because something looked off and "
  "say nothing about overall rates.")
P("")
P("**Exploratory (defined after looking, so not a test):** the AI-flagged 'box on the bedding' boxes in the two fixed-camera Dim_HM "
  "clips occupy one small image region. Counting own frames whose person box falls inside that region "
  f"(envelope cx/cy/w/h = {[[round(a, 3), round(b, 3)] for a, b in sig['envelope_cx_cy_w_h']]}):")
P("")
P("| clip | provenance | frames | frames with a person box in the region |")
P("|---|---|---|---|")
for k, v in sig["counts_by_clip_provenance"].items():
    c, p = k.split(" | ")
    if "Dim_HM" in c:
        P(f"| {c} | {p} | {v['frames']} | {pct(v['signature'], v['frames'])} |")
P("| Sitting_Dim_HM / Standing_Walking_Dim_HM | hand-drawn (round6_patch) | 384 | 0 (no row in raw/bedding_signature.json) |")
P("")
P("The region test is only meaningful inside those two clips (same fixed camera). Hits in other clips are a different room and "
  "camera and are listed in raw/bedding_signature.json only for completeness. The region is a box envelope, so it can also "
  "contain a correct box of a person who really is lying there; it is a pointer, not a count of errors.")
P("")

# look-first list
order = {"UNCLEAR": 0, "BAD_BOX": 1}
cand = [r for r in sheet if r["verdict_ai"] in order]
by_clip = defaultdict(list)
for r in sorted(cand, key=lambda r: (order[r["verdict_ai"]], int(r["idx"]))):
    by_clip[r["source"]].append(r)
look = [r for r in cand if r["verdict_ai"] == "UNCLEAR"]
while len(look) < 32 and any(by_clip.values()):       # round-robin across clips for variety
    for c in list(by_clip):
        if by_clip[c]:
            r = by_clip[c].pop(0)
            if r not in look:
                look.append(r)
        if len(look) >= 32:
            break
extra = sorted((r for r in imgs.values() if r.get("checked") == "True" and r["n_missing"] not in ("", "0")
                and "Dim_HM" not in r["clip"] and r["filename"] not in {x["filename"] for x in sheet}),
               key=lambda r: -float(r["missing_max_conf"] or 0))[:8]
with open(OUT / "look_first.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["rank", "filename", "source", "why", "audit_idx"])
    k = 0
    for r in look:
        k += 1
        w.writerow([k, r["filename"], r["source"], f"AI {r['verdict_ai']} (unverified): {r['notes_ai'][17:]}", r["idx"]])
    for r in extra:
        k += 1
        w.writerow([k, r["filename"], r["clip"], f"not in the sample; SUSPECTED_MISSING at conf {float(r['missing_max_conf']):.2f} outside the Dim_HM clips", ""])
P("## (e) Reading")
P("")
P((OUT / "READING.md").read_text(encoding="utf-8").strip() if (OUT / "READING.md").exists() else "(READING.md missing)")
P("")
P("### Look at these first (also in look_first.csv)")
P("")
for row in list(csv.reader(open(OUT / "look_first.csv", encoding="utf-8")))[1:]:
    P(f"{row[0]}. `{row[1]}` -- {row[2]}{' (sheet idx ' + row[4] + ')' if row[4] else ''}: {row[3]}")
P("")
P("Decisions: DECISIONS.md. Per-image data: train_images.csv. Raw: raw/.")
(OUT / "AUDIT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(OUT / "AUDIT.md")
