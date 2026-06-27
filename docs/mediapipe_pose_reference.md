# MediaPipe Pose Estimation API Reference

This document details the MediaPipe Pose Landmarker Tasks API coordinates, structure, properties, and landmark mapping for the SAGE project.

---

## 1. PoseLandmarkerResult Structure

The `PoseLandmarkerResult` is the returned object from calling `detector.detect(image)`. It contains the following main attributes:

- **`pose_landmarks`**: A list of lists of normalized landmark objects.
  - Each list corresponds to a detected person (typically index `0` represents the primary tracked person).
  - Contains exactly **33** joints (landmarks), indexed from 0 to 32.
- **`pose_world_landmarks`**: Represents the 3D coordinates in physical meters with the origin at the hips center.
- **`segmentation_masks`**: Optional image masks indicating the background vs. foreground person pixels (if segmentation is enabled).

---

## 2. Landmark Property Breakdown

For each landmark $i$ in the 33 detected points, MediaPipe returns five values:

### Normalized Coordinate Space (`x`, `y`, `z`)
- **`x`**: Horizontal pixel coordinate normalized by the image width. It falls within `[0.0, 1.0]`.
  - `0.0` represents the left edge of the image frame.
  - `1.0` represents the right edge of the image frame.
- **`y`**: Vertical pixel coordinate normalized by the image height. It falls within `[0.0, 1.0]`.
  - `0.0` represents the top edge of the image frame.
  - `1.0` represents the bottom edge of the image frame.
- **`z`**: Depth coordinate representing landmark depth, with the midpoint of the hips as the origin coordinate `0.0`.
  - Negative values (`z < 0`) mean the landmark is closer to the camera than the hips center.
  - Positive values (`z > 0`) mean the landmark is further away from the camera than the hips center.
  - *Note: `z` is not a metric measurement in normalized coordinates, but is proportional to the width.*

### Confidence Indicators (`visibility`, `presence`)
- **`visibility`**: A float in the range `[0.0, 1.0]` representing the confidence that the landmark is **visible** (i.e., not occluded by a body part, clothing, or furniture).
  - High value indicates the landmark is clearly visible in the image.
  - Low value indicates the landmark is hidden or covered.
- **`presence`**: A float in the range `[0.0, 1.0]` representing the confidence that the landmark is **present** in the image frame boundary (i.e., not cropped out or outside the field of view).

---

## 3. Landmark Index Mapping

The 33 pose landmarks are arranged sequentially:

| Index | Landmark Name | Description |
|---|---|---|
| **0** | `NOSE` | Center of the nose tip |
| **1** | `LEFT_EYE_INNER` | Left eye inner corner |
| **2** | `LEFT_EYE` | Center of the left eye |
| **3** | `LEFT_EYE_OUTER` | Left eye outer corner |
| **4** | `RIGHT_EYE_INNER` | Right eye inner corner |
| **5** | `RIGHT_EYE` | Center of the right eye |
| **6** | `RIGHT_EYE_OUTER` | Right eye outer corner |
| **7** | `LEFT_EAR` | Left ear tragus point |
| **8** | `RIGHT_EAR` | Right ear tragus point |
| **9** | `MOUTH_LEFT` | Left corner of the lips |
| **10** | `MOUTH_RIGHT` | Right corner of the lips |
| **11** | `LEFT_SHOULDER` | Left shoulder joint acromion |
| **12** | `RIGHT_SHOULDER` | Right shoulder joint acromion |
| **13** | `LEFT_ELBOW` | Left elbow joint lateral epicondyle |
| **14** | `RIGHT_ELBOW` | Right elbow joint lateral epicondyle |
| **15** | `LEFT_WRIST` | Left wrist radial styloid |
| **16** | `RIGHT_WRIST` | Right wrist radial styloid |
| **17** | `LEFT_PINKY` | Left pinky finger tip |
| **18** | `RIGHT_PINKY` | Right pinky finger tip |
| **19** | `LEFT_INDEX` | Left index finger tip |
| **20** | `RIGHT_INDEX` | Right index finger tip |
| **21** | `LEFT_THUMB` | Left thumb tip |
| **22** | `RIGHT_THUMB` | Right thumb tip |
| **23** | `LEFT_HIP` | Left hip joint center |
| **24** | `RIGHT_HIP` | Right hip joint center |
| **25** | `LEFT_KNEE` | Left knee joint center |
| **26** | `RIGHT_KNEE` | Right knee joint center |
| **27** | `LEFT_ANKLE` | Left ankle lateral malleolus |
| **28** | `RIGHT_ANKLE` | Right ankle lateral malleolus |
| **29** | `LEFT_HEEL` | Left heel calcaneus |
| **30** | `RIGHT_HEEL` | Right heel calcaneus |
| **31** | `LEFT_FOOT_INDEX` | Left foot big toe tip |
| **32** | `RIGHT_FOOT_INDEX` | Right foot big toe tip |

---

## 4. Skeleton Connection Topology

Joint landmarks are connected by lines (bones) to construct a full body skeletal wireframe. The structure consists of:

- **Torso Quadrilateral**: `Shoulders (11-12) -> Hips (23-24) -> Shoulders`
- **Face details**: Connect eyes, nose, ears, mouth to trace head boundaries.
- **Limbs**:
  - Left Arm: `Shoulder (11) -> Elbow (13) -> Wrist (15) -> Fingers (17/19/21)`
  - Right Arm: `Shoulder (12) -> Elbow (14) -> Wrist (16) -> Fingers (18/20/22)`
  - Left Leg: `Hip (23) -> Knee (25) -> Ankle (27) -> Heel (29) -> Toe (31)`
  - Right Leg: `Hip (24) -> Knee (26) -> Ankle (28) -> Heel (30) -> Toe (32)`
