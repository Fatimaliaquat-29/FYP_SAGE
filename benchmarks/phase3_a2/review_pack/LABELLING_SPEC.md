# S.A.G.E. person-box labelling spec — v0.1 DRAFT (needs group sign-off)

Put in the repo as `docs/LABELLING_SPEC.md` once agreed. Everyone who draws or reviews a person box follows this page.

## Why this exists
The hand-drawn rounds (round5/round6/round6_patch/round6_heldout) were drawn without a written rule. In the 16 frames checked on 2026-10-14 the rule differed between clips (see "Evidence"). The held-out set is the yardstick for every model, so it must follow one rule.

## Scope
Class `person` only for now. Furniture/object boxes keep today's behaviour.

## Rules (person)
1. **One box per person, per frame.** Tightest axis-aligned rectangle around the person pixels you can see (head, torso, limbs). Do not extend it to guessed hidden parts. Missing toes, feet or legs do NOT stop you drawing a box: the box ends where the visible person ends. The test is "can I identify a person here", not "is the whole body visible".
2. **Cut by frame edge:** box stops at the frame edge.
3. **Occluded by an object (chair, bed edge, furniture):** box the visible part only, and tag `occ=heavy` if less than about half the body is visible. If no body part can be identified (head, hand, foot, clothing), draw no box. The ~half threshold is a starting guess; revisit after the pilot.
4. **Under a blanket (D1 = KEEP, decided by Hussain):** box the outline of the covered body and tag `cover=blanket`. Use the video: if you watched the person get under the blanket and they have not left, the lump is the person. A rumpled blanket on an empty bed gets NO box. Blanket frames are trained on but scored in their own row, never pooled with uncovered frames.
5. **Lying / fallen:** box all visible body including limbs, not just the torso.
6. **Dark frames:** label on a brightened copy (gamma ~0.5 or CLAHE), never on the raw dark image alone. Tag `lowlight=1`. If the person is still not identifiable, tag `unsure=1` and draw no box.
7. **Unsure about anything:** tag `unsure=1`. Unsure frames are excluded from training AND scoring. Do not guess.
8. **No copying person boxes between frames** unless the person is verifiably static. Static furniture boxes may be copied.
9. **Not a person:** reflections, posters, TV screens, mannequins.
10. **Several people:** one box each; overlaps allowed.

## Tags (sidecar CSV, not YOLO classes)
`frame, box_id, occ (none|partial|heavy), cover (none|blanket), lowlight (0|1), unsure (0|1)`

Scoring must report recall per tag combination, never one pooled number.

## Evidence behind this draft (16 frames, small sample)
- `Blanket_Cover_HM` (train, round6): all 26 sampled label files contain a person box, including frames where the body is under the blanket. Visible in overlays: the box sits on the blanket-covered body outline.
- `Behind_Chair_HM` (train, round6): all 11 sampled label files contain a person box. In frame 710 the box matches the chair's extent while the person is crouched behind it.
- `Behind_Bed_HM_000700` (held-out): a very small box (about 7.6% x 7.2% of the frame) on the only visible part. This is a visible-part-only rule, unlike the chair frame.
- `Laying_Dim_HM` (held-out): in frames 400, 800, 1200 a box sits on a near-black region. At review resolution the person is not independently visible, so these boxes cannot be verified without a brightened view.
