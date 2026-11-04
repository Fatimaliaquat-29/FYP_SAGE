"""
benchmarks/rf_maxsamples_sweep.py
=================================
Sweeps max_samples in {0.6, 0.65, 0.7, 0.75, 0.8} against the baseline (max_samples=None)
with all other hyperparameters kept fixed (min_samples_leaf=20, max_features=0.1, n_estimators=300).

Evaluates:
1. Train accuracy (real+synthetic)
2. Validation split accuracy (real only, fold 0)
3. Train-val gap
4. Real-footage accuracy & macro F1 on Hussain Testing (19 clips)
5. Real-footage accuracy & macro F1 on Sanawar Testing (9 clips)
6. Fall-detection recall and false positives on both corpora.
"""

import json
import pickle
import sys
import tempfile
from pathlib import Path
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sklearn.ensemble import RandomForestClassifier
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

CACHE_FILE = REPO_ROOT / "benchmarks" / "results" / "_keypoint_cache.pkl"


def load_production_split():
    """Fold-0 StratifiedGroupKFold split, identical to rf_trainer.py."""
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


def train_and_save_candidate(name, max_samples_val, split_data, tmp_dir: Path):
    X_train, y_train, X_val, y_val, classes, window_size, n_features, train_col_medians = split_data
    X_train_flat = flatten_windows(X_train)
    X_val_flat = flatten_windows(X_val)

    model = RandomForestClassifier(
        n_estimators=300,
        min_samples_leaf=MIN_SAMPLES_LEAF,
        max_features=MAX_FEATURES,
        max_samples=max_samples_val,
        n_jobs=-1,
        random_state=42,
    )
    model.fit(X_train_flat, y_train)
    train_acc = model.score(X_train_flat, y_train)
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
    return model_path, encoder_path, train_acc, val_acc


def main():
    print("Discovering real-footage clips...")
    all_clips = []
    corpus_of = {}
    for corpus_name, corpus_dir in CORPORA.items():
        clips = discover_clips(str(corpus_dir))
        all_clips.extend(clips)
        for _, _, clip_name in clips:
            corpus_of[clip_name] = corpus_name
    print(f"  {len(all_clips)} clips total: " + ", ".join(f"{k}={sum(1 for c in corpus_of.values() if c==k)}" for k in CORPORA))

    cached_keypoints = {}
    if CACHE_FILE.exists():
        print(f"Loading cached keypoints from {CACHE_FILE}...")
        with open(CACHE_FILE, "rb") as f:
            cached_keypoints = pickle.load(f)
    else:
        print("Extracting keypoints once per clip...")
        for video_path, gt_path, clip_name in all_clips:
            cached_keypoints[clip_name] = extract_keypoints(video_path)
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "wb") as f:
            pickle.dump(cached_keypoints, f)
        print(f"Saved keypoints cache to {CACHE_FILE}")

    cached_gt = build_ground_truth_cache(all_clips, cached_keypoints)

    print("Loading production split (fold 0)...")
    split_data = load_production_split()

    sweep_configs = [
        ("baseline (None)", None),
        ("max_samples=0.60", 0.60),
        ("max_samples=0.65", 0.65),
        ("max_samples=0.70", 0.70),
        ("max_samples=0.75", 0.75),
        ("max_samples=0.80", 0.80),
    ]

    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        reports_dir = tmp_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        for name, ms_val in sweep_configs:
            print(f"\n{'='*70}\nRunning Candidate: {name}\n{'='*70}")
            model_path, encoder_path, train_acc, val_acc = train_and_save_candidate(
                name, ms_val, split_data, tmp_dir
            )
            print(f"  Train Acc: {train_acc*100:.2f}% | Val Acc: {val_acc*100:.2f}% | Gap: {(train_acc - val_acc)*100:.2f}pp")

            clf = RFPostureClassifier(model_path=model_path, encoder_path=encoder_path)
            per_corpus = {}
            for corpus_name, corpus_dir in CORPORA.items():
                clips = [c for c in all_clips if corpus_of[c[2]] == corpus_name]
                res = evaluate_model(
                    f"{name} [{corpus_name}]", clf, clips, cached_keypoints, cached_gt,
                    reports_dir
                )
                if not res["available"]:
                    per_corpus[corpus_name] = {"error": "model unavailable"}
                    continue
                metrics = _classification_metrics(res["gt_labels"], res["pred_labels"])
                fall_metrics = _fall_recall(res["fall_results"])
                per_corpus[corpus_name] = {
                    "accuracy": metrics["accuracy"],
                    "macro_f1": metrics["report"]["macro avg"]["f1-score"],
                    "fall_recall": fall_metrics["recall"],
                    "fall_fp": fall_metrics["fp"],
                }
                clf.reset_state()

            results[name] = {
                "max_samples": ms_val,
                "train_acc": train_acc,
                "val_acc": val_acc,
                "gap": train_acc - val_acc,
                "per_corpus": per_corpus,
            }

    print("\n\n" + "=" * 110)
    print("MAX_SAMPLES SWEEP RESULTS SUMMARY")
    print("=" * 110)
    print(f"{'Config':<20} | {'Train Acc':<10} | {'Val Acc':<9} | {'Train-Val Gap':<13} | {'Hussain Acc':<11} | {'Hussain F1':<10} | {'Sanawar Acc':<11} | {'Sanawar F1':<10} | {'Hussain Fall Rec/FP':<20}")
    print("-" * 110)
    for name, r in results.items():
        huss = r["per_corpus"].get("Hussain", {})
        san = r["per_corpus"].get("Sanawar", {})
        h_acc = f"{huss['accuracy']*100:.1f}%" if "accuracy" in huss else "N/A"
        h_f1 = f"{huss['macro_f1']:.3f}" if "macro_f1" in huss else "N/A"
        s_acc = f"{san['accuracy']*100:.1f}%" if "accuracy" in san else "N/A"
        s_f1 = f"{san['macro_f1']:.3f}" if "macro_f1" in san else "N/A"
        h_fall = f"{huss.get('fall_recall', 0)*100:.0f}% / {huss.get('fall_fp', 0)} FP" if "fall_recall" in huss else "N/A"

        print(f"{name:<20} | {r['train_acc']*100:>8.2f}% | {r['val_acc']*100:>7.2f}% | {r['gap']*100:>11.2f}pp | {h_acc:>11} | {h_f1:>10} | {s_acc:>11} | {s_f1:>10} | {h_fall:<20}")
    print("=" * 110)

    # Dump JSON for report reference
    out_json = REPO_ROOT / "benchmarks" / "results" / "rf_max_samples_sweep.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Results saved to {out_json}")


if __name__ == "__main__":
    main()
