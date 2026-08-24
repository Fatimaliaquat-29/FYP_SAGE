# Dimensionality-reduction comparison (5-fold)

StratifiedGroupKFold (grouped by sequence_id). Latency = single-row transform()/predict_proba(), matching real per-frame inference. RF classifier stages timed with n_jobs forced to 1 (matches production src/posture/rf/rf_classifier.py).

| Candidate | Accuracy | Macro F1 | Fit time (s) | Transform p95 (ms) | Classify p95 (ms) | Total p95 (ms) | Size (KB) |
|---|---|---|---|---|---|---|---|
| pca(n=50)+rf | 0.7454 | 0.6059 | 5.7 | 1.055 | 53.985 | 55.674 | 9639.4 |
| pca(n=50)+hgb | 0.7397 | 0.6111 | 7.4 | 1.156 | 28.238 | 29.243 | 2527.1 |
| pca(n=100)+rf | 0.7510 | 0.6145 | 11.3 | 1.133 | 48.303 | 49.186 | 10136.9 |
| pca(n=100)+hgb | 0.7544 | 0.6408 | 14.9 | 1.253 | 48.275 | 49.740 | 3374.9 |
| pca(n=200)+rf | 0.7492 | 0.6095 | 20.9 | 2.030 | 60.151 | 61.486 | 11534.6 |
| pca(n=200)+hgb | 0.7538 | 0.6182 | 21.8 | 1.717 | 30.735 | 33.343 | 5045.6 |
| agglom(n=50)+rf | 0.7621 | 0.6351 | 80.6 | 0.980 | 53.705 | 54.560 | 8797.6 |
| agglom(n=50)+hgb | 0.7573 | 0.6646 | 78.0 | 1.054 | 19.930 | 20.847 | 1793.6 |
| agglom(n=100)+rf | 0.7568 | 0.6361 | 80.7 | 0.923 | 50.842 | 52.130 | 7834.4 |
| agglom(n=100)+hgb | 0.7523 | 0.6617 | 83.2 | 0.880 | 15.404 | 16.650 | 1606.3 |
| agglom(n=200)+rf | 0.7591 | 0.6528 | 88.6 | 0.867 | 47.305 | 48.094 | 7419.1 |
| agglom(n=200)+hgb | 0.7482 | 0.6564 | 88.0 | 0.992 | 17.716 | 18.539 | 1634.9 |
| randproj(n=50)+rf | 0.7463 | 0.6043 | 4.6 | 1.049 | 56.394 | 57.569 | 9882.2 |
| randproj(n=50)+hgb | 0.7483 | 0.6429 | 5.9 | 0.987 | 20.843 | 21.651 | 2255.8 |
| randproj(n=100)+rf | 0.7510 | 0.6204 | 8.5 | 0.966 | 50.476 | 51.292 | 10181.6 |
| randproj(n=100)+hgb | 0.7487 | 0.6470 | 8.1 | 1.140 | 24.618 | 25.547 | 3044.5 |
| randproj(n=200)+rf | 0.7545 | 0.6251 | 16.8 | 1.376 | 59.865 | 60.803 | 11335.2 |
| randproj(n=200)+hgb | 0.7560 | 0.6596 | 13.1 | 1.185 | 17.058 | 18.450 | 4749.4 |
| baseline_rf_no_reduction **(no-reduction baseline)** | 0.7761 | 0.6858 | 263.9 | 0.000 | 70.236 | 70.236 | 6272.2 |
| baseline_hgb_no_reduction **(no-reduction baseline)** | 0.7739 | 0.6929 | 199.6 | 0.000 | 21.092 | 21.092 | 5927.6 |

## Ruled out without CV

- **t-SNE**: no `.transform()` for new points -- every embedding is refit from scratch on whatever data is in hand; placing one new real-time window requires either refitting on old+new data (incompatible with single-window inference) or a second approximation model trained on this same ~56-sequence-scarce dataset. Not run.
- **Kernel PCA**: exact out-of-sample transform needs the training set (or a stored subset) kept in memory and kernel-evaluated on every real-time prediction -- a heavier, different inference-time dependency than every other candidate here. Not run.

## Verdict

Best overall by accuracy/macro F1: **baseline_rf_no_reduction** (acc=0.7761, macro_f1=0.6858).

No reduced-dimensionality candidate matched/beat its same-classifier no-reduction baseline on accuracy AND macro F1 while also being <= on latency and size. Dimensionality reduction is not recommended for this feature space based on this evidence.
