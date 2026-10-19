"""Build the round6_heldout retag review pack (Phase 3, Part B).

Read-only on the source: reads handlabels/round6_heldout/{images,labels} and
writes only under benchmarks/phase3_a2/review_pack/. No model is used; boxes
drawn are exactly the current label files.

Usage: python make_review_pack.py
"""
import csv
import html
import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
SRC = ROOT / "handlabels" / "round6_heldout"
PACK = ROOT / "benchmarks" / "phase3_a2" / "review_pack"
OVL = PACK / "overlays"

CLASSES = ["person", "bottle", "cup", "wine glass", "bowl", "chair", "couch", "bed",
           "dining table", "toilet", "tv", "sink", "refrigerator"]
LUMA_THRESHOLD = 80.0  # frames with mean luma below this (0-255) get a brightened panel
GAMMA = 0.5
CLAHE_CLIP, CLAHE_TILE = 2.0, (8, 8)

PERSON_BGR = (0, 0, 255)
OTHER_BGR = [(255, 200, 0), (0, 220, 255), (255, 0, 255), (0, 255, 0), (255, 128, 0),
             (128, 255, 255), (200, 120, 255), (0, 160, 255), (255, 255, 0), (160, 255, 160),
             (255, 160, 160), (180, 180, 255)]


def clip_of(stem):
    return re.sub(r"_\d+$", "", stem)


def read_labels(path):
    boxes, problems = [], []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 5:
            problems.append(f"line {i}: {len(parts)} fields")
            continue
        try:
            cid = int(parts[0])
            cx, cy, w, h = map(float, parts[1:])
        except ValueError:
            problems.append(f"line {i}: unparsable")
            continue
        if not 0 <= cid < len(CLASSES):
            problems.append(f"line {i}: class id {cid} out of range")
        boxes.append((cid, cx, cy, w, h))
    return boxes, problems


def brighten(img):
    lut = np.array([((i / 255.0) ** GAMMA) * 255 for i in range(256)], dtype=np.uint8)
    g = cv2.LUT(img, lut)
    lab = cv2.cvtColor(g, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=CLAHE_CLIP, tileGridSize=CLAHE_TILE).apply(l)
    return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)


def draw(img, boxes):
    out = img.copy()
    H, W = out.shape[:2]
    thick = max(3, round(min(H, W) / 200))
    thin = max(1, thick // 3)
    font_scale = max(0.5, min(H, W) / 1400)
    # others first, person last so the red box is never hidden
    for cid, cx, cy, w, h in sorted(boxes, key=lambda b: b[0] == 0):
        x1, y1 = int((cx - w / 2) * W), int((cy - h / 2) * H)
        x2, y2 = int((cx + w / 2) * W), int((cy + h / 2) * H)
        if cid == 0:
            cv2.rectangle(out, (x1, y1), (x2, y2), PERSON_BGR, thick)
        else:
            col = OTHER_BGR[(cid - 1) % len(OTHER_BGR)]
            cv2.rectangle(out, (x1, y1), (x2, y2), col, thin)
            name = CLASSES[cid] if 0 <= cid < len(CLASSES) else f"id{cid}"
            (tw, th), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)
            ty = max(th + 2, y1 - 3)
            cv2.rectangle(out, (x1, ty - th - 2), (x1 + tw + 2, ty + 2), (0, 0, 0), -1)
            cv2.putText(out, name, (x1 + 1, ty), cv2.FONT_HERSHEY_SIMPLEX, font_scale, col, 1, cv2.LINE_AA)
    return out


def label_panel(img, text):
    cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
    return img


def main():
    OVL.mkdir(parents=True, exist_ok=True)
    images = sorted((SRC / "images").glob("*.jpg"))
    rows, problems_all, lumas = [], [], []
    for p in images:
        stem, clip = p.stem, clip_of(p.stem)
        img = cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            problems_all.append(f"{p.name}: could not decode")
            continue
        lbl = SRC / "labels" / f"{stem}.txt"
        if lbl.exists():
            boxes, probs = read_labels(lbl)
            problems_all += [f"{lbl.name}: {x}" for x in probs]
        else:
            boxes = []
            problems_all.append(f"{stem}: no label file")
        luma = float(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).mean())
        lumas.append((clip, luma))
        bright = ("dim" in clip.lower()) or luma < LUMA_THRESHOLD
        panel = label_panel(draw(img, boxes), f"original  luma={luma:.1f}")
        if bright:
            panel = np.hstack([panel, label_panel(draw(brighten(img), boxes),
                                                  f"gamma {GAMMA} + CLAHE(L)  [display only]")])
        ok, buf = cv2.imencode(".jpg", panel, [cv2.IMWRITE_JPEG_QUALITY, 88])
        if not ok:
            problems_all.append(f"{stem}: jpg encode failed")
            continue
        buf.tofile(str(OVL / f"{stem}.jpg"))
        person = [b for b in boxes if b[0] == 0]
        rows.append({
            "frame": stem, "clip": clip, "n_person_boxes": len(person),
            "person_boxes_yolo(normalised)": "; ".join(f"{cx:.6f} {cy:.6f} {w:.6f} {h:.6f}"
                                                       for _, cx, cy, w, h in person),
            "mean_luma": f"{luma:.2f}", "brightened_shown": int(bright),
            "box_fits_spec": "", "occ": "", "cover": "", "lowlight": "", "unsure": "", "notes": "",
            "_w": img.shape[1], "_h": img.shape[0], "_n_other": len(boxes) - len(person),
        })

    cols = ["frame", "clip", "n_person_boxes", "person_boxes_yolo(normalised)", "mean_luma",
            "brightened_shown", "box_fits_spec", "occ", "cover", "lowlight", "unsure", "notes"]
    with open(PACK / "review_sheet.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(rows)

    write_html(rows)

    # luma report
    def stats(vals):
        a = np.array(vals)
        return {"n": len(a), "min": round(float(a.min()), 2), "p10": round(float(np.percentile(a, 10)), 2),
                "p25": round(float(np.percentile(a, 25)), 2), "median": round(float(np.median(a)), 2),
                "p75": round(float(np.percentile(a, 75)), 2), "p90": round(float(np.percentile(a, 90)), 2),
                "max": round(float(a.max()), 2), "n_below_threshold": int((a < LUMA_THRESHOLD).sum())}
    report = {"threshold_used": LUMA_THRESHOLD, "rule": "brightened if 'dim' in clip name (case-insensitive) OR mean luma < threshold",
              "gamma": GAMMA, "clahe_clip": CLAHE_CLIP, "clahe_tile": list(CLAHE_TILE),
              "all": stats([l for _, l in lumas]),
              "per_clip": {c: stats([l for cc, l in lumas if cc == c]) for c in sorted({c for c, _ in lumas})},
              "frames_written": len(rows), "brightened_shown": sum(r["brightened_shown"] for r in rows),
              "frames_with_0_person_boxes": sum(1 for r in rows if r["n_person_boxes"] == 0),
              "frames_with_2plus_person_boxes": sum(1 for r in rows if r["n_person_boxes"] >= 2),
              "label_problems": problems_all}
    (PACK / "luma_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if len(rows) == len(images) else 1


def write_html(rows):
    clips = sorted({r["clip"] for r in rows})
    data = [{"f": r["frame"], "c": r["clip"], "np": r["n_person_boxes"], "no": r["_n_other"],
             "l": r["mean_luma"], "b": r["brightened_shown"]} for r in rows]
    page = HTML_TEMPLATE.replace("__DATA__", json.dumps(data)).replace(
        "__CLIPS__", json.dumps(clips)).replace("__N__", str(len(rows))).replace(
        "__THR__", html.escape(str(LUMA_THRESHOLD)))
    (PACK / "index.html").write_text(page, encoding="utf-8")


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Heldout Retag Review</title>
<style>
:root{--bg:#fafaf8;--fg:#1d1d1b;--muted:#6b6b66;--card:#fff;--line:#deddd8;--acc:#b3261e}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--fg:#ecebe6;--muted:#9a9993;--card:#20201e;--line:#34332f;--acc:#ff6b5e}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}
header{position:sticky;top:0;z-index:2;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 16px;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
h1{font-size:16px;margin:0 12px 0 0}.prov{color:var(--acc);font-weight:600}
select,button,label{font:inherit}button{padding:4px 10px;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:6px;cursor:pointer}
main{padding:12px 16px}.meta{color:var(--muted);font-size:13px}
#viewer{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px;margin-bottom:16px}
#viewer img{width:100%;height:auto;display:block;background:#000}
#vtitle{font-weight:600;font-family:ui-monospace,Consolas,monospace}
.clip h2{font-size:15px;margin:18px 0 6px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:6px}
.t{border:2px solid transparent;border-radius:6px;cursor:pointer;background:var(--card);padding:2px}.t.on{border-color:var(--acc)}
.t img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block}.t span{font:11px ui-monospace,Consolas,monospace;color:var(--muted);display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.flag{color:var(--acc)}
</style></head><body>
<header>
<h1>round6_heldout review (__N__ frames)</h1>
<span class="prov">PROVISIONAL labels: draft spec v0.1</span>
<label>Clip <select id="clip"><option value="">all</option></select></label>
<label><input type="checkbox" id="onlyflag"> only 0 or 2+ person boxes</label>
<button id="prev">&larr; prev</button><button id="next">next &rarr;</button>
<span class="meta">Keys: &larr; / &rarr;. Thick red = person; thin = other classes. Right panel (when shown) = gamma+CLAHE, display only. Brightened: clip name has "Dim" or luma &lt; __THR__.</span>
</header>
<main>
<div id="viewer"><div id="vtitle"></div><div class="meta" id="vmeta"></div><img id="vimg" alt=""></div>
<div id="list"></div>
</main>
<script>
const D=__DATA__, CLIPS=__CLIPS__;
let view=D.slice(), idx=0;
const $=id=>document.getElementById(id);
CLIPS.forEach(c=>{const o=document.createElement('option');o.value=c;o.textContent=c+' ('+D.filter(d=>d.c===c).length+')';$('clip').appendChild(o)});
function filt(){const c=$('clip').value,f=$('onlyflag').checked;view=D.filter(d=>(!c||d.c===c)&&(!f||d.np!==1));idx=0;renderList();show()}
function show(){const d=view[idx];if(!d){$('vtitle').textContent='no frames';$('vimg').removeAttribute('src');$('vmeta').textContent='';return}
$('vimg').src='overlays/'+encodeURIComponent(d.f)+'.jpg';$('vtitle').textContent=(idx+1)+' / '+view.length+'  '+d.f;
$('vmeta').innerHTML='clip '+d.c+' &middot; person boxes <span class="'+(d.np!==1?'flag':'')+'">'+d.np+'</span> &middot; other boxes '+d.no+' &middot; mean luma '+d.l+(d.b?' &middot; brightened panel shown':'');
document.querySelectorAll('.t').forEach(t=>t.classList.toggle('on',t.dataset.f===d.f));}
function renderList(){const L=$('list');L.innerHTML='';const by={};view.forEach((d,i)=>{(by[d.c]=by[d.c]||[]).push([d,i])});
Object.keys(by).sort().forEach(c=>{const s=document.createElement('section');s.className='clip';s.innerHTML='<h2>'+c+' ('+by[c].length+')</h2>';const g=document.createElement('div');g.className='grid';
by[c].forEach(([d,i])=>{const t=document.createElement('div');t.className='t';t.dataset.f=d.f;t.innerHTML='<img loading="lazy" alt="" src="overlays/'+encodeURIComponent(d.f)+'.jpg"><span>'+d.f+(d.np!==1?' <b class=flag>['+d.np+'p]</b>':'')+'</span>';t.onclick=()=>{idx=i;show();window.scrollTo({top:0,behavior:'smooth'})};g.appendChild(t)});
s.appendChild(g);L.appendChild(s)})}
$('clip').onchange=filt;$('onlyflag').onchange=filt;
$('prev').onclick=()=>{if(idx>0){idx--;show()}};$('next').onclick=()=>{if(idx<view.length-1){idx++;show()}};
document.addEventListener('keydown',e=>{if(e.target.tagName==='SELECT')return;if(e.key==='ArrowLeft')$('prev').click();if(e.key==='ArrowRight')$('next').click()});
renderList();show();
</script></body></html>
"""

if __name__ == "__main__":
    sys.exit(main())
