# Gait Analysis / Fall-Risk Literature Review

Written for `GAIT_hussain`'s pulled-forward scope (see
`docs/IMPLEMENTATION_PLAN.md` Section 3) as part of implementing
`src/gait/`. This is a condensed review to ground the four candidate
signals implemented in `src/gait/gait_features.py`, not an exhaustive
survey — treat it as a starting point for the project's Phase 1 literature
matrix, not a finished thesis literature chapter. Searches were run
2026-08 via general web search; verify citations independently before
using them in any formal writeup.

## 1. Gait speed

Gait speed is one of the most widely used fall-risk indicators in clinical
practice because it's simple to measure, but a recent individual-participant-
data meta-analysis found its predictive accuracy as a *standalone* screening
tool is only modest — slower gait speed is consistently associated with
increased fall risk/rate, but discriminative accuracy alone is low. The
World Falls Guidelines commonly cited cut-point is <0.8 m/s; the same
meta-analysis suggests a <1.0 m/s cut-point may identify more true fallers
in community-dwelling and clinical settings. Gait speed is explicitly
recommended as *part of* a comprehensive evaluation, not a sufficient
screen by itself, and some research finds it has *lower* discriminative
power than step-width variability for medial-lateral instability
specifically.

**Relevance to this implementation**: `compute_walking_speed()` in
`gait_features.py` is a body-scale-normalized proxy (torso-lengths/second),
not meters/second — there is no camera/subject calibration anywhere in
this pipeline, so the literature's absolute cut-points (0.8-1.0 m/s) cannot
be applied directly. This is used as one signal among several, consistent
with the literature's own recommendation against using it alone.

Sources:
- [Predictive accuracy of gait speed for falls: An individual participant data meta-analysis](https://www.sciencedirect.com/science/article/abs/pii/S1568163726001996)
- [Associations between gait speed and well-known fall risk factors among community-dwelling older adults](https://pubmed.ncbi.nlm.nih.gov/30198603/)
- [Predicting falls in older adults: an umbrella review of instruments assessing gait, balance, and functional mobility](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9310405/)
- [Predicting fall risk through step width variability at increased gait speed in community dwelling older adults](https://www.nature.com/articles/s41598-025-02128-2)

## 2. Stride-time / step-width variability

Several reviewed sources report that step-to-step variability measures are
*more* sensitive to fall risk than gait speed alone. Increased stride-time
coefficient of variation is associated with elevated fall risk (studied in
both MS patients and controls, and separately in frail/cognitively-impaired
populations under dual-task conditions), and is reported as related to
postural sway — i.e. these two signals are not fully independent measures
of the same underlying instability.

**Relevance to this implementation**: `compute_stride_regularity()`
estimates a coefficient of variation from ankle-height oscillation
peak-timing (a *video-derived spatial* proxy for stride periodicity), not
an IMU-derived stride-*time* measurement the way the cited studies compute
it. This project's own validation (synthetic steady vs. unsteady walking,
see `docs/GAIT_DATA_ASSESSMENT.md`) found this proxy's typical scale
(~0.15-0.35) is roughly 4-6x larger than the ~0.05 figure informally
associated with IMU stride-time-CV literature — the risk-mapping threshold
in `gait_risk.py::_stride_cv_risk` was calibrated to this proxy's own
observed scale, not the IMU literature's absolute number, precisely
because reusing the literature's number directly saturated the risk
function and destroyed its ability to discriminate anything (a real bug
caught during this session's validation, documented in the code).

Sources:
- [Stride-Time Variability and Fall Risk in Persons with Multiple Sclerosis](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4710909/)
- [Gait stability and variability measures show effects of impaired cognition and dual tasking in frail people](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3034676/)

## 3. Postural sway

Wearable-sensor fall-risk-assessment reviews flag trunk/postural stability
(sway) during quiet standing as among the most relevant kinematic
parameters for fall-risk detection, alongside gait speed and stride-to-
stride variability, which the same literature calls among the most
powerful predictors of morbidity, mortality, and functional decline more
broadly (not fall risk specifically).

**Relevance to this implementation**: `compute_postural_sway()` measures
standard deviation of hip-center position (torso-lengths) during
sub-windows where the person isn't substantially translating — a rough,
2D-video proxy for the accelerometer/center-of-pressure sway measures in
the cited wearable-sensor literature. No population baseline exists in
this codebase to calibrate an absolute threshold against.

Sources:
- [Wearable Sensor Systems for Fall Risk Assessment: A Review](https://www.frontiersin.org/journals/digital-health/articles/10.3389/fdgth.2022.921506/full)
- [A Systematic Review of Wearable Sensor-Based Technologies for Fall Risk Assessment in Older Adults](https://pmc.ncbi.nlm.nih.gov/articles/PMC9504041/)
- [Gait as a vital sign: integrating wearables and AI into vestibular and balance medicine](https://pmc.ncbi.nlm.nih.gov/articles/PMC12971410/)

## 4. Sit-to-stand time / Timed Up and Go

The Timed-Up-and-Go (TUG) test — stand from a chair, walk 3m, turn, walk
back, sit down, timed with a stopwatch — is described as a gold-standard
clinical fall-risk screening tool. Reported cut-offs: >9.5s flags elevated
risk for ages 65-74 (70.2% sensitivity / 57.0% specificity), >10.5s for
75+ (81.8% sensitivity / 66.7% specificity). A self-administered video-based
version has also been validated against the in-person version (r=0.716,
ICC=0.82), which is methodologically encouraging for a camera-based
approach like this one. The five-times-sit-to-stand test is also used as a
related, narrower fall-risk screen focused specifically on the sit-to-stand
component.

**Relevance to this implementation**: `compute_sit_to_stand()` measures
only the sit-to-stand *phase* (not the full walk-turn-sit TUG sequence),
via duration and a direction-reversal count as a smoothness proxy. Absolute
TUG cut-offs (9.5s/10.5s) are for the *entire* TUG sequence, not just
standing up, so they are not applied as thresholds here — `gait_risk.py`
uses its own heuristic, uncalibrated duration/smoothness scale instead.

Sources:
- [Validity and Reliability of the Self-Administered Timed Up and Go Test in Assessing Fall Risk in Community-Dwelling Older Adults](https://pmc.ncbi.nlm.nih.gov/articles/PMC12101206/)
- [The ability of timed-up and go test and five times sit-to-stand test to screen risk of fall in well-functioning elderly](https://li01.tci-thaijo.org/index.php/journalup/article/view/247051)

## 5. Overall implication for this implementation

No single signal reviewed above is independently sufficient for fall-risk
screening — the consistent theme across sources is that gait speed, stride
variability, sway, and functional-mobility tests (TUG/sit-to-stand) are
complementary, and combining them outperforms any one alone. This directly
supports `GaitRiskAssessor`'s design of blending whichever of the four
signals are actually available in a given window (see `gait_risk.py`),
rather than relying on a single measurement — though this project's
implementation is a rule-based first pass with **no clinical validation
data behind its specific weights or thresholds** (see
`docs/GAIT_DATA_ASSESSMENT.md`), consistent with
`docs/IMPLEMENTATION_PLAN.md`'s own recommendation to start simple given
the lack of gait-specific training data.
