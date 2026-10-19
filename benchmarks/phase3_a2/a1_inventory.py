"""A1 inventory + provenance for sage_merged_v7 train split. READ-ONLY on all inputs.

Writes only:
  benchmarks/phase3_a2/a1_provenance.csv   one row per train image
  benchmarks/phase3_a2/a1_inventory.json   summary tables

Provenance of a train label (own_ prefix only; coco_/empty_ cannot be hand-drawn):
  base stem = stem without 'own_' prefix and without trailing '_rN' repeat suffix.
  hand_byte   : a handlabels/<round>/labels/<base>.txt exists and is byte-identical
  hand_canon  : same file exists; bytes differ but the boxes are identical after the
                canonical formatting the pipeline applies (handlabels.py: int class,
                %.6f coords, blank lines dropped, order kept)
  stem_mismatch : same stem exists in a round but the boxes differ  -> AMBIGUOUS
  no_hand     : no hand label with that stem in any round -> MediaPipe/auto label
Also checks content matches to hand labels under a DIFFERENT stem (similar-name test).
"""
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
DS = ROOT / "datasets" / "sage_merged_v7"
OUT = ROOT / "benchmarks" / "phase3_a2"
ROUNDS = ["round5", "round6", "round6_patch"]
HELDOUT = "round6_heldout"
TARGET_CLIPS = {"Sitting_Dim_HM", "Standing_Walking_Dim_HM"}
STEM_RE = re.compile(r"^(?P<prefix>own|coco|empty)_(?P<rest>.+?)(?:_r(?P<rep>\d+))?$")
FRAME_RE = re.compile(r"^(?P<clip>.+)_(?P<frame>\d{6})$")


def canon(text):
    out = []
    for raw in text.splitlines():
        t = raw.strip()
        if not t:
            continue
        p = t.split()
        if len(p) != 5:
            return ("MALFORMED", t)
        try:
            out.append(f"{int(float(p[0]))} " + " ".join(f"{float(v):.6f}" for v in p[1:]))
        except ValueError:
            return ("MALFORMED", t)
    return tuple(out)


def main():
    hand = {}  # stem -> (round, bytes, canon)
    hand_by_canon = defaultdict(list)
    dup_stems = []
    for r in ROUNDS + [HELDOUT]:
        for p in sorted((ROOT / "handlabels" / r / "labels").glob("*.txt")):
            if p.name == "classes.txt":
                continue
            b = p.read_bytes()
            c = canon(b.decode("utf-8"))
            if p.stem in hand:
                dup_stems.append((p.stem, hand[p.stem][0], r))
            hand[p.stem] = (r, b, c)
            if c:  # empty label files would match every empty label; skip for content search
                hand_by_canon[c].append((r, p.stem))

    rows = []
    pattern = Counter()
    clip_rep = defaultdict(Counter)
    for img in sorted((DS / "images" / "train").glob("*")):
        stem = img.stem
        m = STEM_RE.match(stem)
        prefix = m.group("prefix") if m else "OTHER"
        rest = m.group("rest") if m else stem
        rep = int(m.group("rep")) if (m and m.group("rep")) else 0
        fm = FRAME_RE.match(rest)
        clip = fm.group("clip") if fm else rest
        pattern[(prefix, "repeat" if rep else "base")] += 1
        if prefix == "own":
            clip_rep[clip][f"r{rep}" if rep else "base"] += 1
        lbl = DS / "labels" / "train" / f"{stem}.txt"
        lb = lbl.read_bytes() if lbl.exists() else None
        lc = canon(lb.decode("utf-8")) if lb is not None else None
        prov, rnd, other = "not_own", "", ""
        if prefix == "own":
            if rest in hand:
                rnd, hb, hc = hand[rest]
                if lb == hb:
                    prov = "hand_byte"
                elif lc == hc:
                    prov = "hand_canon"
                else:
                    prov = "stem_mismatch"
            else:
                prov = "no_hand"
            if lc and lc in hand_by_canon:
                others = [f"{r}/{s}" for r, s in hand_by_canon[lc] if s != rest]
                other = ";".join(others[:3])
        n_person = sum(1 for line in (lc or ()) if isinstance(line, str) and line.startswith("0 "))
        rows.append({"stem": stem, "prefix": prefix, "clip": clip, "base_stem": rest,
                     "repeat_copy": rep, "has_label": int(lb is not None),
                     "label_sha256": hashlib.sha256(lb).hexdigest() if lb is not None else "",
                     "n_boxes": len(lc) if isinstance(lc, tuple) else 0, "n_person": n_person,
                     "provenance": prov, "hand_round": rnd, "content_match_other_stem": other,
                     "target_clip": int(clip in TARGET_CLIPS)})

    # repeat copies must carry the same label as their base
    by_base = defaultdict(list)
    for r in rows:
        by_base[(r["prefix"], r["base_stem"])].append(r)
    rep_label_mismatch = [k for k, v in by_base.items() if len({x["label_sha256"] for x in v}) > 1]
    rep_without_base = [k for k, v in by_base.items() if not any(x["repeat_copy"] == 0 for x in v)]

    with open(OUT / "a1_provenance.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    own = [r for r in rows if r["prefix"] == "own"]
    per_round = Counter((r["hand_round"], r["provenance"], "repeat" if r["repeat_copy"] else "base")
                        for r in own if r["hand_round"])
    hand_stems_in_train = {r["base_stem"] for r in own if r["provenance"] in ("hand_byte", "hand_canon")}
    round_coverage = {}
    for rd in ROUNDS + [HELDOUT]:
        stems = {s for s, v in hand.items() if v[0] == rd}
        val_stems = {p.stem[4:] for p in (DS / "labels" / "val").glob("own_*.txt")}
        round_coverage[rd] = {"hand_label_files": len(stems),
                              "base_frames_in_train_matched": len(stems & hand_stems_in_train),
                              "stems_in_train_any_content": len(stems & {r["base_stem"] for r in own}),
                              "stems_in_val": len(stems & val_stems),
                              "stems_absent_from_train_and_val": len(stems - {r["base_stem"] for r in own} - val_stems)}
    target = [r for r in rows if r["target_clip"]]
    tgt = Counter((r["clip"], r["provenance"], "repeat" if r["repeat_copy"] else "base") for r in target)
    # val split: target clips present?
    val_target = Counter()
    for p in (DS / "images" / "val").glob("own_*"):
        fm = FRAME_RE.match(re.sub(r"_r\d+$", "", p.stem[4:]))
        if fm and fm.group("clip") in TARGET_CLIPS:
            val_target[fm.group("clip")] += 1

    summary = {
        "train_images": len(rows),
        "pattern_counts": {f"{a}/{b}": n for (a, b), n in sorted(pattern.items())},
        "max_repeat_index": max(r["repeat_copy"] for r in rows),
        "repeat_suffix_values": dict(Counter(r["repeat_copy"] for r in rows)),
        "own_clips": {c: dict(v) for c, v in sorted(clip_rep.items())},
        "own_provenance": dict(Counter(r["provenance"] for r in own)),
        "per_round_provenance": {f"{a}|{b}|{c}": n for (a, b, c), n in sorted(per_round.items())},
        "round_coverage": round_coverage,
        "target_clips_train": {f"{a}|{b}|{c}": n for (a, b, c), n in sorted(tgt.items())},
        "target_clips_val_images": dict(val_target),
        "content_match_other_stem_count": sum(1 for r in own if r["content_match_other_stem"]),
        "content_match_other_stem_examples": [(r["stem"], r["content_match_other_stem"]) for r in own if r["content_match_other_stem"]][:10],
        "repeat_label_mismatch_groups": len(rep_label_mismatch),
        "repeat_without_base_groups": len(rep_without_base),
        "missing_label_files": sum(1 for r in rows if not r["has_label"]),
        "hand_duplicate_stems_across_rounds": dup_stems,
        "heldout_stems_in_train": sorted({r["base_stem"] for r in own if r["hand_round"] == HELDOUT})[:20],
    }
    (OUT / "a1_inventory.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
