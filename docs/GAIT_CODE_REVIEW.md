# GAIT Analysis — Code Review

Scope: `src/gait/gait_features.py`, `src/gait/gait_risk.py`, `src/gait/gait_stream.py`,
plus their actual inputs (`src/posture/pipeline_utils.py`'s `is_landmark_valid`/
`_compute_hip_angle`/`_classify_heuristic`, `src/posture/lstm/lstm_features.py`'s
`normalize_frame`) and their tests (`tests/test_gait_risk.py`,
`tests/test_gait_stream.py`). **Analysis and reporting only — no code was
modified.** Random Forest code (`src/posture/rf/`) was not opened or touched.

**Standing caveat**: every real-footage clip referenced anywhere in this
document is a self-recorded video of a single (N=1) subject. No finding
here generalizes to a population — see `docs/GAIT_DATA_ASSESSMENT.md`'s
own standing caveat for the same statement applied project-wide.

## How the pipeline actually flows (traced, not assumed)

```
MediaPipe landmarks -> pipeline_utils.build_pose_row() -> {timestamp, keypoints}
    -> RingFrameBuffer (gait_stream.py, live case) or a plain list (batch case)
    -> GaitRiskAssessor.assess_risk(window)
         -> _raw_keypoint_array / _torso_scaled_hip_track / _timestamps  (computed ONCE, shared)
         -> compute_walking_speed | compute_stride_regularity | compute_postural_sway | compute_sit_to_stand
         -> each signal's risk-mapping sigmoid (_speed_risk / _stride_cv_risk / _sway_risk / _sit_to_stand_risk)
         -> weighted average over whichever signals were `available`
    -> {"risk_score": float|None, "signals": [4 entries]}
```

`gait_features.py` reuses `lstm_features.normalize_frame` for hip-centered
shape features and duplicates (not imports) two numeric thresholds from
`pipeline_utils._classify_heuristic` — this dual relationship (reuse one
module fully, duplicate constants from another) is where several of the
findings below come from.

---

## 1. Critical / High-Priority Problems

| # | Severity | File / Function | Problem | Why It Is a Problem | Recommended Improvement |
|---|---|---|---|---|---|
| 1 | **High** | `gait_features.py::compute_stride_regularity` | No ambulation/stationarity gate. `compute_walking_speed` requires `MIN_AMBULATION_PATH`+`MIN_AMBULATION_COHERENCE`; `compute_postural_sway` requires a "not translating" sub-window check. `compute_stride_regularity` has neither — it only requires ≥50% ankle-visibility coverage and ≥3 `find_peaks` detections, with **no height/prominence threshold** on those peaks. | A stationary subject with ordinary ankle jitter (weight-shifting, MediaPipe frame-to-frame noise) can produce ≥3 spurious local maxima ≥5 frames apart and yield a fabricated CV value, which then enters `risk_score` at weight **1.2 — the highest weight of all four signals**. This is exactly the "stationary subject reads as gait" failure class that the other two position-based signals were explicitly hardened against (see their own docstrings/`MIN_AMBULATION_PATH`'s comment: *"a perfectly stationary person... reads as extremely slow gait speed... a real bug caught in this module's own smoke testing"*) — the same bug class was fixed for `walking_speed` and `postural_sway` but not for `stride_regularity`. **Confirmed zero test coverage**: no test method anywhere in `tests/test_gait_risk.py` references `stride_regularity`/`compute_stride_regularity` at all, which is consistent with this gap never having been exercised. | Add a gate mirroring the other two signals (e.g. require the same ambulation path/coherence check already computed for `walking_speed`, or add `find_peaks(..., prominence=...)`/height threshold scaled to the ankle-oscillation amplitude expected during real gait). Add a test with a stationary+jittery window analogous to `AmbulationCoherenceTests`. |
| 2 | **High** | `gait_features.py::compute_walking_speed` / `MIN_AMBULATION_COHERENCE` | The ambulation gate checks path length and net/path coherence, but never checks translation **direction**. A coherent, high-net-displacement, purely *vertical* motion (e.g. kneeling down) satisfies the same gate as genuine horizontal locomotion. | Confirmed on real footage this project already has (`Kneeling.MOV`): the kneel-down phase reads as 0.32-0.54 torso-lengths/sec "walking speed" with risk_contribution 0.80-0.89 — a stationary, non-ambulatory posture change materially raising `risk_score`. | Add a horizontal-dominance check on the already-computed hip track (e.g. require `|dx| > |dy|` for the dominant component of net displacement) before trusting the path as ambulation. Needs real varied-angle walking footage to validate the added gate doesn't also suppress genuine walking recall (see `docs/GAIT_CALIBRATION_DATASET_PLAN.md` Section 3 Table 2, `kneel` scenario). |
| 3 | **High** | `gait_features.py::compute_sit_to_stand` (state definition) | Hip-angle-only geometric degeneracy: a deep bend or squat produces the same shoulder-hip-knee angle signature as sitting on a chair, since both fold the torso over the hips. | Confirmed on real footage: `compute_sit_to_stand`'s primary path fires on several `Bend_pickup_squat_*`/`Bend_pickup_*_leftRight`/`_back` clips whose ground truth never contains a "Sitting" state — a genuine false-positive class, not a hypothetical one. Pre-existing (confirmed identical before/after this session's landmark-confidence fix), not a new regression. | Needs an additional discriminating signal (duration, translation-toward-a-fixed-point, or knee-angle in combination — see Finding 4 below) validated against matched bend-vs-sit footage before any threshold change (see calibration plan Category D). |

---

## 2. Correctness & Logic Issues

| # | Severity | File / Function | Problem | Why It Is a Problem | Recommended Improvement |
|---|---|---|---|---|---|
| 4 | **Medium** | `gait_features.py` module comment (~L104-110) vs. `pipeline_utils.py::_classify_heuristic` (~L786-837) | GAIT's sitting/standing state machine (used by `compute_sit_to_stand`) classifies purely on **hip angle**. The project's own canonical posture classifier, `_classify_heuristic`, requires **both** `hip_angle >= 143` **and** `knee_angle >= 143` for "Standing" (and *either* `<= 125` for "Sitting"). gait_features.py's comment says it "mirrors" `_classify_heuristic`'s thresholds — true only of the two numeric constants, not of the underlying two-angle rule. | A posture where the torso is upright but a knee is bent (mid-stride, one leg raised, an asymmetric stance) can register as GAIT-"Standing" while the project's own posture classifier would not call the same frame "Standing." This is a real behavioral divergence between two parts of the same pipeline that both claim to reason about "standing"/"sitting," not merely a documentation nit. | Either explicitly document hip-angle-only as a deliberate, cheaper simplification (not a mirror of `_classify_heuristic`), or fold in `knee_angle` the same way, if closer behavioral consistency across the two modules is wanted. |
| 5 | **Medium** | `gait_features.py::_batch_hip_angle` vs. `pipeline_utils.py::_compute_hip_angle` | `_batch_hip_angle`'s docstring claims to be a "Vectorized equivalent of pipeline_utils._compute_hip_angle... gated by the same per-point validity rule." In fact `_compute_hip_angle` itself only checks for `None`/NaN on its three points — it has **no** `[-margin, 1+margin]` range check. `_batch_hip_angle` additionally applies `_batch_landmark_valid` (NaN **and** range), which `_compute_hip_angle` never does. | For a non-NaN but wildly out-of-frame-range landmark (a MediaPipe extrapolation artifact), the two functions genuinely disagree: `_compute_hip_angle` computes an angle from it; `_batch_hip_angle` rejects it as invalid. GAIT's behavior is arguably the more defensible one, but the docstring's equivalence claim is not numerically accurate, which could mislead a future maintainer into assuming the two always agree. | Reword the docstring to state this is a deliberate strengthening (added range gating on top of `_compute_hip_angle`'s math), not a byte-identical port. |
| 6 | **Medium** | `gait_features.py` — `_HIP_ANGLE_SITTING_MAX`/`_HIP_ANGLE_STANDING_MIN` vs. `pipeline_utils.py` — `ANGLE_SITTING_MAX`/`ANGLE_STANDING_MIN` | The two constant pairs are manually duplicated (not imported/shared) across files. They currently match (125.0/143.0, verified in both files as of this review) — but `pipeline_utils.py`'s copies are marked `# TODO-tune-further-if-needed` by their own author, i.e. explicitly flagged as likely to change. No test, assertion, or shared constant exists to catch future drift. | If a teammate retunes `pipeline_utils.py`'s values (plausible — your teammate is actively working on the posture/RF side of this project right now) without knowing `gait_features.py` keeps its own copy, GAIT's sit/stand detection would silently start using stale thresholds with no error, no warning, no test failure. | Add a regression test asserting the two constant pairs stay equal (import `pipeline_utils` only for the comparison, not for runtime use, respecting the existing "don't edit pipeline_utils.py" boundary) so drift fails CI loudly instead of degrading GAIT silently. |
| 7 | **Medium** | `gait_features.py::compute_sit_to_stand` | Only the **first** confirmed sit→stand transition in a window is ever reported (`first_stand_after = stand_runs[0][0]`, unconditionally). A window containing two full cycles (sit→stand→sit→stand — e.g. someone attempting to stand, failing, sitting back down, trying again) silently reports only the first. | In the live streaming case (`gait_stream.py`'s sliding window) a later re-assessment will eventually surface the second cycle once the first scrolls out of the buffer, so this isn't a total blind spot over a session — but any single `assess_risk()` call cannot reflect "repeated attempts," which is itself a clinically meaningful pattern the current output has no way to represent. | Document the single-transition-per-window contract more prominently in the docstring (currently implied, not stated). Consider whether a repeated-attempt count is worth adding as a future signal. |
| 8 | **Medium** | `gait_risk.py::GaitRiskAssessor._validate_window` / `gait_features.py::_timestamps` | No explicit check that `window` frames are in non-decreasing timestamp order. Most downstream math degrades gracefully on simple single-swap disorder (`dt_positive` gates, `duration_sec <= 0` rejections), but `_confirmed_runs`' state-run detection operates on array-index order only, not verified chronological order — more complex disorder could produce a *positive but wrong* `duration_sec`/`reversal_count` rather than a caught error. | This is an implicit, load-bearing assumption across the whole module with no assertion anywhere. A caller bug (e.g. a race in a multi-threaded frame producer feeding `gait_stream.py`) would silently produce a plausible-looking but incorrect number instead of a clear failure. | Add an explicit monotonicity check (hard error or at least a debug-mode assertion) in `_validate_window` or `_timestamps`. |

---

## 3. Data / Feature Processing Issues

| # | Severity | File / Function | Problem | Why It Is a Problem | Recommended Improvement |
|---|---|---|---|---|---|
| 9 | **Medium** | `gait_features.py::compute_postural_sway` | Non-overlapping tiling (`range(0, n - stable_subwindow + 1, stable_subwindow)`) drops any trailing `n % stable_subwindow` frames entirely, and tile boundaries are phase-locked to the passed-in window's start index (index 0), not to any absolute clock. | For the two window sizes actually used elsewhere in this codebase (90, 150 — both exact multiples of 15) no data is lost, but any other window length silently drops up to 14 trailing frames from consideration. Separately, because `gait_stream.py` uses a *sliding* window, the same real 15-frame span of quiet standing can land in different tile boundaries across consecutive re-assessments purely because the window's start index shifted — so the reported sway value can vary slightly call-to-call from tiling phase alone, not from any real change in the subject. | Either document the phase-sensitivity as an accepted approximation, or use an overlapping/finer-stride tiling so boundary placement matters less. |
| 10 | **Low** | `gait_features.py::_timestamps` | Falls back to `i / 30.0` for any row with a missing/non-numeric `timestamp`, with no logging if the fallback actually fires. Consistent with `pipeline_utils._compute_velocity`'s own convention (good — consistent with the rest of the pipeline), but silent. | Since every GAIT signal is time-dependent (`dt` divides into every speed/duration calculation), a caller that doesn't populate real timestamps would silently produce numbers calibrated for the wrong frame rate, with no diagnostic trace to detect it after the fact. | Consider a one-time (not per-frame) warning if the fallback path is taken for a non-trivial fraction of a window. |

---

## 4. Edge Cases & Robustness

| # | Severity | File / Function | Problem | Why It Is a Problem | Recommended Improvement |
|---|---|---|---|---|---|
| 11 | **Medium** | `gait_features.py::compute_sit_to_stand` (camera/geometry dependence) | Hip-angle thresholds are fixed degree values measured in 2D image space; camera angle and seat geometry directly change the *apparent* hip angle for the same real-world posture. | Confirmed real miss this session: `Sit_Stand_AnklesInvisible.MOV`'s ground truth confirms a genuine seated period (1-4.9s), but the computed hip_angle never drops below ~156° throughout the entire clip — well above the 125° sitting threshold — so `compute_sit_to_stand` never fires at all for a real, GT-confirmed sit-to-stand event. A **false negative**, not a noise artifact. | Needs footage from multiple camera angles for the same real sit-to-stand motion (calibration plan Section 8) to characterize how much the threshold needs to vary by viewing angle, or whether a different/relative measure is needed. |
| 12 | **Low** | `gait_features.py::_drop_runs_after_long_gap` | A confirmed run starting at index 0 of the window is never treated as "emerging from a blackout" (the backward gap-scan terminates immediately, since there's no data before the window to inspect). | Inherent boundary limitation, not really fixable (no information exists before the window starts) — but it does mean `_MAX_TRUSTED_GAP_BEFORE_STATE`'s protection has a blind spot specifically at the first few frames of any window. | Document explicitly; no code fix is meaningfully possible without look-behind data the function doesn't have. |
| 13 | **Low** | `gait_features.py::_peak_translation_speed` | `np.nanmean` on a slice that can be entirely NaN emits an unhandled `RuntimeWarning: Mean of empty slice` to stderr, even though the subsequent `np.isfinite` check correctly handles the resulting NaN with no wrong output. | Cosmetic, not a correctness bug — but noisy in production logs and could bury a more important warning during debugging. | Wrap in `np.errstate` or pre-check `np.all(np.isnan(...))` before calling `nanmean`. |
| 14 | **Low** | `gait_stream.py::RingFrameBuffer.snapshot` | Returns a shallow `list()` copy of the deque — new list, same underlying row-dict/array objects. No current caller mutates a `keypoints` array in place after appending it, but nothing structurally prevents it either. | If a future caller did reuse/mutate a buffer in place, previously-buffered "historical" frames could silently change underneath an in-flight assessment. Not observed anywhere in the current codebase. | A one-line docstring note about the aliasing assumption is enough given no current violation exists; not worth a deep copy's overhead pre-emptively. |

---

## 5. Performance Issues

Nothing significant found. This module has already been through two
documented optimization passes (shared `_raw`/`_hip_track`/`_ts` across all
four signal computations, vectorized `_batch_hip_angle` replacing a
per-frame Python loop, vectorized `_normalized_positions`) — `assess_risk()`
measures ~2-6ms end-to-end for a realistic 150-frame window
(`benchmarks/profile_gait_pipeline.py`), which is appropriate given this
module runs once per multi-second window, not per video frame.

| # | Severity | File / Function | Problem | Why It Is a Problem | Recommended Improvement |
|---|---|---|---|---|---|
| 15 | **Low** | `gait_features.py::compute_postural_sway` | The sub-window tiling loop is a plain Python `for` loop (not vectorized), unlike the rest of the module. | For the window sizes actually in use (6-10 iterations per call) this is not a measurable cost — flagged only for completeness, not because it matters in practice. | Not worth vectorizing at current window sizes; revisit only if window sizes grow substantially. |

---

## 6. Code Quality / Maintainability

| # | Severity | File / Function | Problem | Why It Is a Problem | Recommended Improvement |
|---|---|---|---|---|---|
| 16 | **Low** | `gait_risk.py::GaitRiskAssessor.assess_risk` | The `if/elif/else` dispatch that decides which shared parameters (`_hip_track` vs. `_raw`) to pass each signal function is keyed by hardcoded signal-name strings; the `else` branch (passing only `_raw`, no `_ts`) is currently **unreachable** dead code, since all 4 entries in `_SIGNAL_SPECS` are covered by the first two branches. | If a 5th signal were ever added to `_SIGNAL_SPECS` without also updating this dispatch, it would silently fall into the untested `else` branch. In practice this wouldn't break anything today, since every `compute_*` function has its own internal `_ts = _ts if _ts is not None else _timestamps(window)` fallback — but it's a maintenance trap that would silently defeat the sharing optimization (redundant recompute) rather than error. | Low priority given the graceful fallback; worth a one-line comment noting the `else` branch is currently unreachable and why. |
| 17 | **Low** | `gait_risk.py::GaitRiskAssessor.assess_risk` / `_SIGNAL_WEIGHTS` | Signal weights (`walking_speed=1.0, stride_regularity=1.2, postural_sway=1.2, sit_to_stand=0.8`) only affect the blend when *multiple* signals are simultaneously available — if only one signal is available for a window (common: `sit_to_stand` availability was ~60% in the last full-corpus run, and other signals are frequently individually unavailable too), that signal's own `risk_contribution` **is** `risk_score`, regardless of its nominal weight (the weight cancels out of a single-term ratio). Mathematically correct, but non-obvious. | Easy to misread the weights as "sit_to_stand always counts less," when in the common single-signal-available case it doesn't count less at all. | A short docstring clarification, no behavior change needed. |

---

## 7. Testing Gaps

- **`compute_stride_regularity` has zero test coverage** — no test method in `tests/test_gait_risk.py` references stride regularity, peak detection, or ankle oscillation at all. This directly explains why Finding #1 (missing ambulation gate) was never caught. **Highest-priority testing gap.**
- **No test exercises `GaitRiskAssessor`'s weight-blending/renormalization logic directly** — e.g. no test asserting "when only `sit_to_stand` is available, `risk_score == sit_to_stand`'s own `risk_contribution`" or "when two signals are available, the blend matches the documented weighted-average formula." The behavior is currently correct (verified by direct code reading), but nothing would catch a regression in the blending arithmetic itself.
- **No test exercises `compute_postural_sway`'s tiling boundary** (a window length not evenly divisible by `stable_subwindow`, to confirm trailing-frame-drop behavior is understood/intended rather than accidental).
- **No test exercises out-of-order or non-monotonic timestamps** anywhere in the GAIT suite (relates to Finding #8).
- `gait_stream.py`'s test coverage (`RingFrameBufferTests`, `StreamingGaitRiskAssessorTests`, `GaitPipelineTests`) is comparatively solid — eviction, cadence, producer non-blocking, queue-drop-under-overload, and clean shutdown are all directly tested. This is a genuine strength, not a gap.

---

## 8. Potential Improvements

- Reuse the already-computed ambulation path/coherence machinery from `compute_walking_speed` inside `compute_stride_regularity` (Finding #1) — the hip-track and validity arrays it would need are already being computed elsewhere in the same `assess_risk()` call.
- A horizontal-dominance check for `compute_walking_speed`'s ambulation gate (Finding #2) — cheap, reuses the already-computed hip track, but needs new footage to validate before shipping (see `docs/GAIT_CALIBRATION_DATASET_PLAN.md`).
- A shared-constant regression test between `gait_features.py` and `pipeline_utils.py` (Finding #6) is a very cheap addition that closes a real silent-drift risk given active parallel work on the posture/RF side of this project.

---

## Final Assessment

**Overall GAIT Analysis Health: Good** — the architecture is sound, extensively documented with real-footage provenance for nearly every threshold, already performance-optimized, and the streaming layer is well-tested. The issues found are real and worth fixing, but they're localized gaps in an otherwise coherent design (one signal missing a gate its siblings have, some cross-module consistency claims that are slightly looser than their docstrings imply, some edge-window behaviors worth documenting more explicitly) rather than a fundamentally broken approach.

- **Critical issues: 0**
- **High issues: 3**
- **Medium issues: 7**
- **Low issues: 7**

**Top 5 to fix first:**
1. **#1 — `compute_stride_regularity`'s missing ambulation gate.** Highest severity, zero test coverage, and it feeds the highest-weighted signal in the entire risk blend (1.2) — the single most consequential gap found.
2. **#2 — `compute_walking_speed`'s missing translation-direction check.** Already has a real, measured false-positive on existing footage (`Kneeling.MOV`) with a documented risk-score impact, not a hypothetical.
3. **#6 — the duplicated-threshold drift risk between `gait_features.py` and `pipeline_utils.py`.** Cheapest fix on this list (one regression test) for a real risk given your teammate is actively changing the posture/RF side right now.
4. **#4/#5 — the two cross-module "equivalence" claims that aren't fully accurate** (hip-angle-only vs. two-angle state definition; `_batch_hip_angle`'s range-gating difference from `_compute_hip_angle`). Both are documentation-accuracy fixes more than behavior fixes, but they're exactly the kind of thing that misleads whoever reads this code next.
5. **#3 — the geometric-degeneracy false positive on bend/squat motion.** Already well-understood and documented as a known limitation from prior sessions; listed here because it remains the most clinically consequential open item (it's a genuine false-positive class on real footage), even though safely fixing it needs new footage rather than a quick patch.

**Areas already well-designed — do not change unnecessarily:**
- The shared `_raw`/`_hip_track`/`_ts` computation pattern in `assess_risk()` (Section 5) — a real, measured, well-documented performance win with no correctness cost.
- `_normalized_positions`'s vectorized equivalence to `lstm_features.normalize_frame` — verified byte-for-byte equivalent by direct comparison of both implementations; this one's docstring claim is accurate.
- The landmark-confidence gating in `_count_reversals` (this session's fix) and the fixed-reference-scale translation guard in `_peak_translation_speed` — both are genuinely subtle, well-reasoned, real-footage-validated mechanisms; resist the urge to "simplify" either without re-deriving the specific failure modes they close off (documented in each function's own docstring).
- `gait_stream.py`'s producer/consumer design (bounded queue, drop-oldest-on-overload, single consumer thread) — appropriately scoped for a single-camera Jetson deployment, well-tested, and honestly documented about what it deliberately does *not* attempt (multi-stream concurrency).

---

## Update (a later session): findings #2 and #3 revisited with real footage

New self-recorded footage (`test_footage/GAIT_Analysis_Test_Footages/`)
was added specifically to close the data gaps this review flagged.
**Finding #2 (walking-direction gate) is now validated**: real walking
footage at 3 camera angles (lateral, diagonal, toward-camera) confirms
`MIN_HORIZONTAL_DOMINANCE_RATIO=1.0` does not over-suppress genuine
walking recall at any of them — see that constant's docstring in
`gait_features.py` for the full measurement. No threshold change.
**Finding #3 (bend/squat vs. sit degeneracy) is narrower than it was** — a
shallow sustained bend (`Shallow_Bending.mov`) correctly never fires. A
deep sustained bend/kneel (`Deep_Bend.mov`) originally produced one
spurious detection, traced to severe self-occlusion — the sit-run and
stand-run were each confirmed by a DIFFERENT single side with no shared
corroborating side between them (unlike a genuine one-sided-occlusion
case, e.g. `SitFloor_lowKeypoints.MOV`, where the SAME side covers both
states). Fixed (a still-later session) via a narrow anchor-run
side-switching guard — see `docs/GAIT_DATA_ASSESSMENT.md` Section 7 for
the full trace and evidence this doesn't regress the 24 other real
detections in the corpus. The ORIGINALLY-suspected mechanism (angle-only
geometric degeneracy on a deep bend tracked with full confidence) remains
open and untested in isolation — this corpus's one deep-bend clip happens
to also be heavily occluded, so the two mechanisms couldn't be tested
apart from each other; `Deep_Bend.mov` still produces fully-confident
(reliability=1.0) detections near its real "Getting up" span that don't
precisely align with GT timing, which is that residual, still-open
mechanism. Separately, this investigation found and fixed a real,
unrelated bug: the
`MIN_STAND_HIP_RISE` guard (added since this review was written) was
wired into `compute_sit_to_stand`'s primary path only, not its fallback
path, so the exact seated-repositioning false positive it was built to
close (`Sit_Stand_2.mov`) still fired via the fallback path in one
window — fixed by extending the same guard there. Full detail in
`docs/GAIT_DATA_ASSESSMENT.md` Section 7.

## Update (a later session): finding #4 — closed via the first option
##    ("document as deliberate"), plus a real, narrower use of knee_angle
##    added since

Took the first of the two recommended fixes: `gait_features.py`'s own
module comment now explicitly states the mirror is of the two DEGREE
VALUES only, not of `_classify_heuristic`'s two-angle decision rule, and
spells out the frame-for-frame divergence this causes (a real, accepted,
not-a-bug difference) — see that comment block, directly above
`_HIP_ANGLE_SITTING_MAX`/`_HIP_ANGLE_STANDING_MIN` in `gait_features.py`.
The second option (fold `knee_angle` into the core Standing/Sitting STATE
definition) was NOT taken — no evidence emerged that it's needed, and
`compute_sit_to_stand`'s own state definition (`sitting_mask`/
`standing_mask`) is still hip-angle-only, unchanged.

Separately (not part of closing this finding, but relevant to it):
`docs/GAIT_DATA_ASSESSMENT.md` Section 13 added a real, narrower use of
`knee_angle` elsewhere in the same function — a standing-bend hip-rise
EXEMPTION guard, reusing `pipeline_utils.py`'s own `ANGLE_STANDING_MIN`
value for a different purpose (deciding whether a hip-rise-guard
rejection should be overridden), not the core state definition this
finding is about. The docstring now distinguishes the two explicitly so a
future reader doesn't mistake the narrow exemption for the broader
two-angle state-definition change this finding always left open.
