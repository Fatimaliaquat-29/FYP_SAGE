"""
benchmarks/rf_methodology_realfootage_confirm.py
==================================================
Decisive real-footage confirmation step for RF methodology candidates
that survived benchmarks/rf_methodology_sweep.py's offline validation-split
screen. This project's own established rule (docs/RF_GENERALIZATION_INVESTIGATION.md
Section 4a/4b, docs/TCN_REGRESSION_REPORT.md): a validation-split win is
NOT adopted until confirmed on both real test_footage/ corpora, because
this project has repeatedly seen validation-split conclusions not hold up
on real footage (summary-stat features, TCN/RF class weighting).

Trains each candidate on the SAME single production split (fold 0 of
StratifiedGroupKFold, same seed) that rf_trainer.py::train() uses -- NOT
the 5-fold sweep -- since that is what actually gets shipped. test_footage/
is used ONLY for scoring here, never for fitting or hyperparameter choice
(the data wall from this loop's own constraints).

Usage:
    python benchmarks/rf_methodology_realfootage_confirm.py
"""
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.rf.rf_trainer import flatten_windows, MIN_SAMPLES_LEAF, MAX_FEATURES, LSTM_DATASET_NPZ
from src.posture.lstm import lstm_features as lf
from src.posture.lstm.lstm_dataset import generate_synthetic_windows, impute_nan
from src.posture.rf.rf_classifier import RFPostureClassifier
from evaluate_real_footage import discover_clips, extract_keypoints
from compare_tcn_lstm import (
    build_ground_truth_cache, evaluate_model, _classification_metrics, _fall_recall,
)

CORPORA = {
    "Sanawar": REPO_ROOT / "test_footage" / "Sanawar Testing 7-22-26",
    "Hussain": REPO_ROOT / "test_footage" / "Hussain Testing 7-30-26",
}


def load_production_split():
    """Fold-0 StratifiedGroupKFold split, real+synthetic train / real-only
    val -- IDENTICAL logic to rf_trainer.py::train()'s own data prep, so a
    candidate's flatten-space performance here matches what shipping it
    via rf_trainer.py would actually produce."""
    from sklearn.model_selection import StratifiedGroupKFold

    data = np.load(str(LSTM_DATASET_NPZ), allow_pickle=True)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.int32)
    groups = data["groups"]
    classes = data["classes"]
    window_size, n_features = X.shape[1], X.shape[2]

    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    train_idx, val_idx = next(sgkf.split(X, y, groups))
    X_val, y_val = X[val_idx], y[val_idx]
    X_train, y_train = X[train_idx], y[train_idx]

    train_col_medians = lf.compute_col_medians(X_train)
    X_train = lf.impute_nan(X_train, train_col_medians)
    X_val = lf.impute_nan(X_val, train_col_medians)

    X_syn, y_syn, _ = generate_synthetic_windows(window_size=window_size, n_per_class=800)
    X_syn = impute_nan(X_syn.astype(np.float32))
    X_train = np.concatenate([X_train, X_syn], axis=0).astype(np.float32)
    y_train = np.concatenate([y_train, y_syn], axis=0).astype(np.int32)
    rng = np.random.default_rng(seed=1)
    shuf = rng.permutation(len(X_train))
    X_train, y_train = X_train[shuf], y_train[shuf]

    return X_train, y_train, X_val, y_val, classes, window_size, n_features, train_col_medians


def train_and_save_candidate(name, make_model, split_data, tmp_dir: Path):
    X_train, y_train, X_val, y_val, classes, window_size, n_features, train_col_medians = split_data
    X_train_flat = flatten_windows(X_train)
    X_val_flat = flatten_windows(X_val)

    model = make_model()
    model.fit(X_train_flat, y_train)
    val_acc = model.score(X_val_flat, y_val)

    import joblib
    safe_name = "".join(c if c.isalnum() else "_" for c in name)
    model_path = tmp_dir / f"{safe_name}.joblib"
    encoder_path = tmp_dir / f"{safe_name}_encoder.json"
    joblib.dump(model, str(model_path))
    encoder = {
        "classes": list(classes),
        "class_to_idx": {c: int(i) for i, c in enumerate(classes)},
        "window_size": int(window_size),
        "n_features": int(n_features),
        "col_medians": train_col_medians.tolist(),
        "feature_representation": "flatten",
        "n_features_out": int(X_train_flat.shape[1]),
    }
    encoder_path.write_text(json.dumps(encoder), encoding="utf-8")
    return model_path, encoder_path, val_acc


def main():
    print("Discovering real-footage clips (both corpora)...")
    all_clips = []
    corpus_of = {}
    for corpus_name, corpus_dir in CORPORA.items():
        clips = discover_clips(str(corpus_dir))
        all_clips.extend(clips)
        for _, _, clip_name in clips:
            corpus_of[clip_name] = corpus_name
    print(f"  {len(all_clips)} clips total: " + ", ".join(f"{k}={sum(1 for c in corpus_of.values() if c==k)}" for k in CORPORA))

    print("Extracting keypoints once per clip (shared across every candidate)...")
    cached_keypoints = {}
    for video_path, gt_path, clip_name in all_clips:
        cached_keypoints[clip_name] = extract_keypoints(video_path)
    cached_gt = build_ground_truth_cache(all_clips, cached_keypoints)

    print("Building production train/val split (fold 0, same as rf_trainer.py)...")
    split_data = load_production_split()

    from sklearn.ensemble import RandomForestClassifier

    # Candidates to confirm on real footage -- populate this list with
    # whatever benchmarks/rf_methodology_sweep.py's offline screen showed
    # as beating the baseline on BOTH val_acc and macro_f1. The baseline
    # itself is always included as the reference point.
    candidates = {
        "baseline (production)": lambda: RandomForestClassifier(
            n_estimators=300, min_samples_leaf=MIN_SAMPLES_LEAF, max_features=MAX_FEATURES,
            n_jobs=-1, random_state=42,
        ),
    }

    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for name, make_model in candidates.items():
            print(f"\n{'='*70}\nCandidate: {name}\n{'='*70}")
            model_path, encoder_path, val_acc = train_and_save_candidate(name, make_model, split_data, tmp_dir)
            print(f"  validation-split accuracy: {val_acc:.4f}")

            clf = RFPostureClassifier(model_path=model_path, encoder_path=encoder_path)
            per_corpus = {}
            for corpus_name, corpus_dir in CORPORA.items():
                clips = [c for c in all_clips if corpus_of[c[2]] == corpus_name]
                res = evaluate_model(f"{name} [{corpus_name}]", clf, clips, cached_keypoints, cached_gt,
                                      tmp_dir / "reports")
                if not res["available"]:
                    per_corpus[corpus_name] = {"error": "model unavailable"}
                    continue
                metrics = _classification_metrics(res["gt_labels"], res["pred_labels"])
                fall_metrics = _fall_recall(res["fall_results"])
                per_corpus[corpus_name] = {
                    "accuracy": metrics["accuracy"],
                    "macro_f1": metrics["report"]["macro avg"]["f1-score"],
                    "sitting_recall": metrics["report"].get("Sitting", {}).get("recall"),
                    "lying_recall": metrics["report"].get("Lying", {}).get("recall"),
                    "fall_recall": fall_metrics["recall"],
                    "fall_false_positives": fall_metrics["fp"],
                }
                clf.reset_state()
            results[name] = {"val_acc": val_acc, "per_corpus": per_corpus}

    print(f"\n\n{'='*100}\nREAL-FOOTAGE CONFIRMATION SUMMARY\n{'='*100}")
    for name, r in results.items():
        print(f"\n{name} (val_acc={r['val_acc']:.4f})")
        for corpus_name, m in r["per_corpus"].items():
            if "error" in m:
                print(f"  {corpus_name}: {m['error']}")
                continue
            print(f"  {corpus_name}: acc={m['accuracy']*100:.1f}% macro_f1={m['macro_f1']:.3f} "
                  f"sitting_recall={m['sitting_recall']:.3f} lying_recall={m['lying_recall']:.3f} "
                  f"fall_recall={m['fall_recall']*100:.1f}% fall_fp={m['fall_false_positives']}")


if __name__ == "__main__":
    main()
