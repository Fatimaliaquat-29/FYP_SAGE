# Real Footage Evaluation - Summary

| Clip | Accuracy % | Fall Result | Flag |
|---|---|---|---|
| Fall_backward_2 | 100.0% | FP frames [90, 91, 92, 93, 94] | **false positive** |
| Fall_backward_3 | 100.0% | FP frames [120, 121, 122, 123, 124] | **false positive** |
| Fall_backward_4 | 100.0% | FP frames [89, 90, 91, 92, 93] | **false positive** |
| Fall_forward_2 | 100.0% | TP (latency 128 frames) |  |
| Fall_from_chair_2 | 100.0% | FP frames [174, 175, 176, 177, 178] | **false positive** |
| Fall_slow_collapse | 100.0% | FP frames [229, 230, 231, 232, 233] | **false positive** |

---

## Fall_backward_2 (**false positive**)

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: nan%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 112 | 0 |

**Fall detection:** FP frames [90, 91, 92, 93, 94]

**Mismatched frames:**

_None_

---

## Fall_backward_3 (**false positive**)

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: nan%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 112 | 0 |

**Fall detection:** FP frames [120, 121, 122, 123, 124]

**Mismatched frames:**

_None_

---

## Fall_backward_4 (**false positive**)

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: nan%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 205 | 0 |

**Fall detection:** FP frames [89, 90, 91, 92, 93]

**Mismatched frames:**

_None_

---

## Fall_forward_2

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: 100.0%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 55 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 52 | 0 |

**Fall detection:** TP (latency 128 frames)

**Mismatched frames:**

_None_

---

## Fall_from_chair_2 (**false positive**)

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: nan%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 46 | 0 |

**Fall detection:** FP frames [174, 175, 176, 177, 178]

**Mismatched frames:**

_None_

---

## Fall_slow_collapse (**false positive**)

**Posture accuracy:** 100.0%

**Per-class accuracy:**

- Standing: nan%
- Sitting: nan%
- Lying: 100.0%

**Confusion matrix:**

| GT \ Pred | Standing | Sitting | Lying | Unknown |
|---|---|---|---|---|
| **Standing** | 0 | 0 | 0 | 0 |
| **Sitting** | 0 | 0 | 0 | 0 |
| **Lying** | 0 | 0 | 178 | 0 |

**Fall detection:** FP frames [229, 230, 231, 232, 233]

**Mismatched frames:**

_None_
