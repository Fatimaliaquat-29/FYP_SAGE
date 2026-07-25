# S.A.G.E. — Fall-Detection Sanity-Check Clip Guide

A recording plan for validating the pipeline against the failure modes it is
actually sensitive to. Each clip targets a specific behaviour we have had to
engineer for. Record them once, keep them as a fixed regression set, and re-run
the whole set after any change to the heuristic or the LSTM.

> **Safety first.** Any "fall" must be onto a thick crash mat / mattress, by a
> fit adult stand-in simulating the motion. **Never** have an elderly person
> actually fall. To imitate an elderly fall, slow the movement down (see the
> "slow crumple" clips) rather than falling harder.

---

## 1. Camera & recording setup (keep identical for every clip)

This should match how the camera will actually be deployed, because the pipeline
is sensitive to viewpoint.

| Setting | Value |
|---|---|
| **Mount height** | ~1.6–2.0 m (wall/corner mount), angled slightly downward |
| **Coverage** | The floor area where a fall could happen must be in frame, so a fallen person stays visible |
| **Framing** | Whole body (head to feet) visible when the person stands at mid-distance |
| **Distance range** | Person acts at ~2–4 m from the camera (plus the dedicated far clip) |
| **Resolution / FPS** | Match the deployment camera; 720p @ 25–30 FPS is fine. **Keep it the same across all clips** |
| **Lighting** | Normal, even room lighting. Avoid strong backlight / windows behind the person |
| **Duration** | 8–15 s per clip. Begin with the person already in frame |
| **One action per clip** | Don't chain multiple activities; one clip = one behaviour |

Record a short spoken or written note per clip: *is there a fall, and roughly at
what second?* You'll need it for the ground-truth file (Section 4).

---

## 2. POSITIVE clips — the system MUST raise a fall alert

| # | Clip | How to perform it | What it stresses |
|---|---|---|---|
| P1 | **Forward trip fall** | Walk, trip, pitch forward onto the mat, end lying prone. Fast. | Baseline fast fall |
| P2 | **Backward fall** | Stand, lose balance backward, land supine. | Fall direction variety |
| P3 | **Sideways collapse** | Stand, buckle sideways to the floor. | Lateral fall |
| P4 | **Slow crumple / "elderly" collapse** ⭐ | Knees slowly buckle, sink to the floor over ~2–3 s, end lying. | **The critical elderly case** — slow falls that don't spike velocity. Relies on the LSTM + sustained-lying, not the fast trigger |
| P5 | **Fall out of a chair** | Seated, slide/collapse off the chair to the floor. | Fall that starts from sitting |
| P6 | **Fall then long lie** | Any fall, then stay motionless on the floor for 10 s+. | Sustained-lying trigger + the alert "hold" |
| P7 | **Off-axis fall (toward/away from camera)** ⭐ | Fall directly toward or away from the lens, not sideways to it. | Hardest geometry — a fall along the camera axis flattens the 2-D trunk angle. If P7 is missed, that's the known weak spot |
| P8 | **Far-distance fall** | Repeat a forward fall at ~4–5 m from the camera. | Scale invariance — small body in frame must still register |
| P9 | **Partially occluded fall** | Fall so the lower body ends up behind a sofa/table (legs hidden). | Occlusion handling (torso-only path) |

⭐ = the clips most likely to expose a regression; prioritise these.

**Expected result:** every P-clip raises a `FALL ALERT` in `realtime_fall_detection.py`
(and scores as a **TP** in `hybrid_evaluate.py`). P4/P7/P8 may detect a bit later
than P1 — that's acceptable as long as they detect within a couple of seconds.

---

## 3. NEGATIVE clips — the system must NOT alert (activities of daily living)

These are where false positives come from. Several map directly to bugs we've fixed.

| # | Clip | How to perform it | What it stresses |
|---|---|---|---|
| N1 | **Sit down normally** | Walk to a chair, sit at a normal pace. | Basic ADL |
| N2 | **Fast flop into a chair/sofa** | Drop quickly into the seat. | Fast sit-down (fixed FP: `Fast_Sit`, `Sit_3`). High angular velocity but stays upright in the seat |
| N3 | **Recline in a chair/sofa** ⭐ | Sit, then lean the torso back to ~50–70° while hips stay on the seat. | Reclined-sit read as "Lying" (fixed FP: `Sit_1`). Relies on the hip-descent guard — hips must not drop |
| N4 | **Lie down on a bed/sofa on purpose** | Stand, then deliberately lie down and rest. | Known tradeoff: prolonged lying after being upright *will* eventually flag (sustained-lying). Record it to confirm the behaviour and timing you're comfortable with |
| N5 | **Bend to pick something up** | Bend forward to the floor, then straighten up. | Torso pitches past horizontal then returns — must not fire |
| N6 | **Squat / kneel** | Crouch to tie a shoelace, then stand. | Low posture that isn't a fall |
| N7 | **Walk around** | Walk across the room, near and far. | Motion without a fall |
| N8 | **Stand still, near then far** | Stand ~1.5 m, then ~4 m from camera. | Scale/posture stability (must stay "Standing" at all distances) |
| N9 | **Sit on the floor, then get up** | Deliberately sit down on the floor, pause, stand back up. | A person on the floor who did *not* fall |
| N10 | **Empty room** | No person in frame for ~10 s. | No spurious detection on an empty scene |

⭐ = the clips most likely to expose a regression; prioritise these.

**Expected result:** no `FALL ALERT`. N4 is the deliberate exception — expect it to
flag after the person has been lying a while; decide whether that latency is
acceptable for your deployment.

---

## 4. How to run the clips through the pipeline

### A. Live-style, with the real-time detector (what a deployment sees)

```bash
# Replay a clip as if it were a live camera feed (debounced alerting):
python realtime_fall_detection.py --input test_footage/P1_forward_fall.mov

# A real webcam instead of a file:
python realtime_fall_detection.py --input 0
```

Watch for the on-screen `FALL DETECTED` banner / console `*** FALL ALERT ***`.
This is the honest end-to-end test: it includes the debounce, so a 1–2 frame
blip will **not** raise an alarm.

### B. Scored, frame-accurate (for the regression table)

```bash
# Batch: put every clip + its *_gt.csv in one folder, then:
python hybrid_evaluate.py --batch_dir sanity_clips --output_dir results/sanity

# Or a single clip:
python hybrid_evaluate.py --video sanity_clips/P1_forward_fall.mov \
                          --ground_truth sanity_clips/P1_forward_fall_gt.csv
```

This prints a per-clip **Heuristic / LSTM / Hybrid** table (TP/FN/FP + latency).

### Ground-truth file format (`<clipname>_gt.csv`)

One row per posture segment: `start_time, end_time, label, ignore`. Times are
`M:SS`. A fall is auto-detected by the scorer when the clip contains an **upright
segment followed by a Lying segment** — you do not mark the fall explicitly.

```csv
"0:00, 0:02, Standing, FALSE"
"0:02, 0:03, Transition, TRUE"
"0:03, 0:05, Lying, FALSE"
```

- `label` ∈ `Standing | Sitting | Lying | Transition`.
- `ignore = TRUE` excludes those (usually transition) frames from posture-accuracy
  scoring — set it TRUE on the brief transition segment.
- **ADL / negative clips:** use only `Standing`/`Sitting` segments and **no Lying
  segment** → the scorer expects no fall, so any detection counts as a false positive.

---

## 5. What "passing" looks like

- **All P-clips → TP** (detected within ~1–2 s). A missed P-clip is a false
  negative — the worst outcome for an elderly-safety system — investigate before
  anything else.
- **All N-clips → no alert.** An N-clip that alerts is a false positive; note
  which trigger fired (`other_labels` in the per-clip CSV: `rapid_fall`,
  `pre_lying_fall`, `sustained_lying`, or `lstm,pred=Fall`) so it can be traced.
- Keep this exact clip set unchanged over time. Re-run it after every heuristic
  or LSTM change — that fixed set is what breaks the "new clip reveals a new bug"
  cycle, because you're always measuring against the same battery.

---

## 6. Tuning knobs (if a clip misbehaves)

| Symptom | Where to look |
|---|---|
| Missed **fast** fall | `FALL_ANGULAR_VELOCITY_FLOOR`, `FALL_PEAK_VELOCITY_FLOOR`, `ANGVEL_SUSTAIN_FRAMES` in `pipeline_utils.py` |
| Missed **slow** fall | `LYING_PERSISTENCE_FRAMES` (sustained-lying latency); LSTM recall |
| FP on **fast sit** | Pre-lying trigger gate (`FALL_PRELYING_ANGVEL_FLOOR`, torso-angle gate) |
| FP on **recline** | `FALL_HIP_DESCENT_MIN` (hip-descent guard) |
| Alerts **flicker / too eager** | `--alert-min-hits`, `--alert-window`, `--alert-hold` on the real-time detector |

All fall thresholds were re-derived from the peak-motion distribution of 96 real
annotated LeFD falls vs 34 ADL clips (not hand-fit to individual test videos), so
prefer re-deriving from data over nudging a constant to make one clip pass.
