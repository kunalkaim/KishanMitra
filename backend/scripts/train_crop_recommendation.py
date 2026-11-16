import os
import sys
import json
import hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Add backend directory to path
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, ".."))
_PROJECT_ROOT = os.path.abspath(os.path.join(_BACKEND_DIR, ".."))
sys.path.insert(0, _BACKEND_DIR)

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    balanced_accuracy_score, confusion_matrix, classification_report,
    log_loss
)

from app.ml.crop_recommendation.preprocessing import (
    load_dataset, split_data, FEATURE_NAMES, RANDOM_STATE
)
from app.ml.crop_recommendation.fuzzy_model import AgronomicFuzzyCropExpert
from app.ml.crop_recommendation.gaussian_nb import GaussianNBCropExpert
from app.ml.crop_recommendation.decision_tree import DecisionTreeCropExpert
from app.ml.crop_recommendation.ensemble import HybridWeightedCropEnsemble
from app.ml.crop_recommendation.explainability import CropExplainabilityEngine
from app.ml.crop_recommendation.model_registry import ModelRegistry, to_json_serializable

REPORTS_DIR = os.path.join(_PROJECT_ROOT, "datasets", "crop_recommendation", "reports")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)


def calculate_metrics(y_true, y_pred, y_probs, classes) -> dict:
    """Calculates comprehensive classification metrics with explicit canonical labels."""
    acc = float(accuracy_score(y_true, y_pred))
    bal_acc = float(balanced_accuracy_score(y_true, y_pred))
    prec_macro = float(precision_score(y_true, y_pred, average='macro', zero_division=0))
    prec_weighted = float(precision_score(y_true, y_pred, average='weighted', zero_division=0))
    rec_macro = float(recall_score(y_true, y_pred, average='macro', zero_division=0))
    rec_weighted = float(recall_score(y_true, y_pred, average='weighted', zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, average='macro', zero_division=0))
    f1_weighted = float(f1_score(y_true, y_pred, average='weighted', zero_division=0))
    
    # Probability metrics
    loss = float(log_loss(y_true, y_probs, labels=classes))
    
    # Brier score convention: Multi-class one-hot mean squared error
    # BS = (1/N) * sum_i sum_c (p_{ic} - y_{ic})^2
    y_indices = np.array([classes.index(label) for label in y_true])
    y_one_hot = np.zeros_like(y_probs)
    y_one_hot[np.arange(len(y_true)), y_indices] = 1.0
    brier = float(np.mean(np.sum((y_probs - y_one_hot) ** 2, axis=1)))

    return {
        "accuracy": acc,
        "balanced_accuracy": bal_acc,
        "precision_macro": prec_macro,
        "precision_weighted": prec_weighted,
        "recall_macro": rec_macro,
        "recall_weighted": rec_weighted,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted,
        "log_loss": loss,
        "brier_score": brier
    }


def plot_confusion_matrix(y_true, y_pred, classes, title, output_filename):
    """Generates and saves a publication-quality confusion matrix."""
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    plt.figure(figsize=(14, 12))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', xticklabels=classes, yticklabels=classes, cbar=False)
    plt.xlabel('Predicted Crop Category', fontsize=11, fontweight='bold')
    plt.ylabel('Ground Truth Crop Category', fontsize=11, fontweight='bold')
    plt.title(title, fontsize=12, fontweight='bold', pad=12)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, output_filename), dpi=200)
    plt.close()


def train_and_evaluate():
    print("==========================================================================")
    print("🌾 KISANMITRA: SCIENTIFIC HYBRID AI CROP RECOMMENDATION PIPELINE (v1.1) 🌾")
    print("==========================================================================")

    # 1. Dataset Ingestion & Validation
    print("\n[Step 1/7] Ingesting dataset and computing SHA-256 integrity hash...")
    X, y, classes = load_dataset()
    classes = sorted(list(classes))
    
    raw_csv_path = os.path.join(_PROJECT_ROOT, "datasets", "crop_recommendation", "raw", "Crop_recommendation.csv")
    dataset_hash = "unknown"
    if os.path.exists(raw_csv_path):
        with open(raw_csv_path, 'rb') as f:
            dataset_hash = hashlib.sha256(f.read()).hexdigest()

    print(f"Dataset records: {len(X)} across {len(classes)} crop classes.")
    print(f"Features: {FEATURE_NAMES}")
    print(f"Raw CSV SHA-256: {dataset_hash}")

    # Leakage-free Stratified Split: 70% Train, 15% Val, 15% Test
    X_train, y_train, X_val, y_val, X_test, y_test = split_data(
        X, y, train_size=0.70, val_size=0.15, test_size=0.15, random_state=RANDOM_STATE
    )

    print(f"Training split:   {len(X_train)} samples ({len(X_train)/len(X)*100:.1f}%) [Used for fitting & Stratified CV]")
    print(f"Validation split: {len(X_val)} samples ({len(X_val)/len(X)*100:.1f}%) [Used exclusively for ensemble weights]")
    print(f"Test split:       {len(X_test)} samples ({len(X_test)/len(X)*100:.1f}%) [UNTOUCHED for final evaluation]")

    # 2. Train Expert 1: Agronomic Fuzzy Logic Model
    print("\n[Step 2/7] Fitting Expert 1: Data-Derived Fuzzy Logic Model (Train split only)...")
    fuzzy_expert = AgronomicFuzzyCropExpert(name="AgronomicFuzzyExpert_v1.1")
    fuzzy_expert.fit(X_train, y_train)

    val_fuzzy_preds = fuzzy_expert.predict(X_val)
    val_fuzzy_probs = fuzzy_expert.predict_proba(X_val)
    val_fuzzy_metrics = calculate_metrics(y_val, val_fuzzy_preds, val_fuzzy_probs, classes)
    print(f"✓ Fuzzy Validation Accuracy: {val_fuzzy_metrics['accuracy']*100:.2f}% | Macro F1: {val_fuzzy_metrics['f1_macro']*100:.2f}%")

    # 3. Train Expert 2: Gaussian Naive Bayes with 5-Fold Stratified CV on Training Split
    print("\n[Step 3/7] Tuning Expert 2: Gaussian Naive Bayes via 5-Fold Stratified CV on Training Split...")
    gnb_expert = GaussianNBCropExpert()
    gnb_cv_results = gnb_expert.tune_with_cross_validation(X_train, y_train, n_splits=5, random_state=RANDOM_STATE)
    print(f"✓ GNB Best var_smoothing (via CV): {gnb_cv_results['best_var_smoothing']:.2e}")
    print(f"✓ GNB Cross-Validation Macro F1:   {gnb_cv_results['best_cv_macro_f1']*100:.2f}%")

    val_gnb_preds = gnb_expert.predict(X_val)
    val_gnb_probs = gnb_expert.predict_proba(X_val)
    val_gnb_metrics = calculate_metrics(y_val, val_gnb_preds, val_gnb_probs, classes)
    print(f"✓ GNB Validation Accuracy:         {val_gnb_metrics['accuracy']*100:.2f}% | Macro F1: {val_gnb_metrics['f1_macro']*100:.2f}%")

    # 4. Train Expert 3: Regularized Decision Tree with 5-Fold Stratified CV on Training Split
    print("\n[Step 4/7] Tuning Expert 3: Decision Tree via 5-Fold Stratified CV on Training Split...")
    dt_expert = DecisionTreeCropExpert(random_state=RANDOM_STATE)
    dt_cv_results = dt_expert.tune_with_cross_validation(X_train, y_train, n_splits=5)
    print(f"✓ DT Best Hyperparameters (via CV): {dt_cv_results['best_params']} (Depth={dt_cv_results['effective_depth']})")
    print(f"✓ DT Cross-Validation Macro F1:      {dt_cv_results['best_cv_macro_f1']*100:.2f}%")

    val_dt_preds = dt_expert.predict(X_val)
    val_dt_probs = dt_expert.predict_proba(X_val)
    val_dt_metrics = calculate_metrics(y_val, val_dt_preds, val_dt_probs, classes)
    print(f"✓ DT Validation Accuracy:            {val_dt_metrics['accuracy']*100:.2f}% | Macro F1: {val_dt_metrics['f1_macro']*100:.2f}%")

    # 5. Build and Optimize Weighted Ensemble on Validation Split
    print("\n[Step 5/7] Optimizing Weighted Ensemble weights on Validation Split (Unconstrained Simplex)...")
    ensemble = HybridWeightedCropEnsemble(fuzzy_expert, gnb_expert, dt_expert, classes=classes)
    opt_report = ensemble.optimize_weights_on_validation(X_val, y_val, step=0.02)

    w1, w2, w3 = ensemble.weights
    val_ens_preds = ensemble.predict(X_val)
    val_ens_probs = ensemble.predict_proba(X_val)
    val_ens_metrics = calculate_metrics(y_val, val_ens_preds, val_ens_probs, classes)

    print(f"✓ Selected Ensemble Weights: W1 (Fuzzy)={w1:.3f}, W2 (GNB)={w2:.3f}, W3 (DT)={w3:.3f}")
    print(f"✓ Ensemble Validation Accuracy: {val_ens_metrics['accuracy']*100:.2f}% | Macro F1: {val_ens_metrics['f1_macro']*100:.2f}%")
    print(f"✓ Equal-Weight Validation F1:   {opt_report['equal_weight_ensemble_validation']['macro_f1']*100:.2f}%")

    # 6. Final Independent Evaluation on UNTOUCHED Test Split
    print(f"\n[Step 6/7] Final Independent Evaluation on UNTOUCHED Test Set (N={len(X_test)})...")
    
    # Expert 1: Fuzzy Test
    test_fuzzy_preds = fuzzy_expert.predict(X_test)
    test_fuzzy_probs = fuzzy_expert.predict_proba(X_test)
    test_fuzzy_metrics = calculate_metrics(y_test, test_fuzzy_preds, test_fuzzy_probs, classes)

    # Expert 2: GNB Test
    test_gnb_preds = gnb_expert.predict(X_test)
    test_gnb_probs = gnb_expert.predict_proba(X_test)
    test_gnb_metrics = calculate_metrics(y_test, test_gnb_preds, test_gnb_probs, classes)

    # Expert 3: DT Test
    test_dt_preds = dt_expert.predict(X_test)
    test_dt_probs = dt_expert.predict_proba(X_test)
    test_dt_metrics = calculate_metrics(y_test, test_dt_preds, test_dt_probs, classes)

    # Equal-Weight Ensemble Test
    eq_test_probs = (test_fuzzy_probs / 3.0) + (test_gnb_probs / 3.0) + (test_dt_probs / 3.0)
    eq_test_preds = np.array([classes[idx] for idx in np.argmax(eq_test_probs, axis=1)])
    test_eq_metrics = calculate_metrics(y_test, eq_test_preds, eq_test_probs, classes)

    # Optimized Weighted Ensemble Test
    test_ens_preds = ensemble.predict(X_test)
    test_ens_probs = ensemble.predict_proba(X_test)
    test_ens_metrics = calculate_metrics(y_test, test_ens_preds, test_ens_probs, classes)

    # Per-class classification report
    clf_report = classification_report(y_test, test_ens_preds, labels=classes, target_names=classes, output_dict=True)

    print("\n" + "="*70)
    print("📈 FINAL INDEPENDENT TEST PERFORMANCE COMPARISON (UNTOUCHED SPLIT)")
    print("="*70)
    print(f"1. Fuzzy Logic Alone:         Accuracy = {test_fuzzy_metrics['accuracy']*100:6.2f}% | Macro F1 = {test_fuzzy_metrics['f1_macro']*100:6.2f}% | Brier = {test_fuzzy_metrics['brier_score']:.4f}")
    print(f"2. Gaussian Naive Bayes Alone:Accuracy = {test_gnb_metrics['accuracy']*100:6.2f}% | Macro F1 = {test_gnb_metrics['f1_macro']*100:6.2f}% | Brier = {test_gnb_metrics['brier_score']:.4f}")
    print(f"3. Decision Tree Alone:       Accuracy = {test_dt_metrics['accuracy']*100:6.2f}% | Macro F1 = {test_dt_metrics['f1_macro']*100:6.2f}% | Brier = {test_dt_metrics['brier_score']:.4f}")
    print(f"4. Equal-Weight Ensemble:     Accuracy = {test_eq_metrics['accuracy']*100:6.2f}% | Macro F1 = {test_eq_metrics['f1_macro']*100:6.2f}% | Brier = {test_eq_metrics['brier_score']:.4f}")
    print(f"5. Optimized Hybrid Ensemble: Accuracy = {test_ens_metrics['accuracy']*100:6.2f}% | Macro F1 = {test_ens_metrics['f1_macro']*100:6.2f}% | Brier = {test_ens_metrics['brier_score']:.4f}")
    print("="*70)

    # 7. Generate Visualizations
    print("\n[Step 7/7] Generating publication-grade visualizations...")
    
    # 5 Confusion Matrices
    plot_confusion_matrix(y_test, test_fuzzy_preds, classes, "Fuzzy Logic Expert: Test Set Confusion Matrix", "01_fuzzy_confusion_matrix.png")
    plot_confusion_matrix(y_test, test_gnb_preds, classes, "Gaussian Naive Bayes Expert: Test Set Confusion Matrix", "02_gnb_confusion_matrix.png")
    plot_confusion_matrix(y_test, test_dt_preds, classes, "Decision Tree Expert: Test Set Confusion Matrix", "03_decision_tree_confusion_matrix.png")
    plot_confusion_matrix(y_test, eq_test_preds, classes, "Equal-Weight Ensemble: Test Set Confusion Matrix", "04_equal_ensemble_confusion_matrix.png")
    plot_confusion_matrix(y_test, test_ens_preds, classes, f"Optimized Hybrid Ensemble: Test Set Confusion Matrix (Acc = {test_ens_metrics['accuracy']*100:.2f}%)", "05_optimized_ensemble_confusion_matrix.png")

    # Plot 6: Model Accuracy & Macro F1 with unclipped dynamic scale [0, 105]
    models = ['Fuzzy Logic', 'Gaussian NB', 'Decision Tree', 'Equal Ensemble', 'Optimized Ensemble']
    accuracies = [
        test_fuzzy_metrics['accuracy']*100, 
        test_gnb_metrics['accuracy']*100, 
        test_dt_metrics['accuracy']*100, 
        test_eq_metrics['accuracy']*100, 
        test_ens_metrics['accuracy']*100
    ]
    f1_scores = [
        test_fuzzy_metrics['f1_macro']*100, 
        test_gnb_metrics['f1_macro']*100, 
        test_dt_metrics['f1_macro']*100, 
        test_eq_metrics['f1_macro']*100, 
        test_ens_metrics['f1_macro']*100
    ]
    
    x_indices = np.arange(len(models))
    width = 0.35

    plt.figure(figsize=(10, 6))
    plt.bar(x_indices - width/2, accuracies, width, label='Test Accuracy (%)', color='#174B35')
    plt.bar(x_indices + width/2, f1_scores, width, label='Test Macro F1 (%)', color='#E8AD45')
    plt.ylabel('Score (%)', fontsize=11, fontweight='bold')
    plt.title('Independent Test Set Performance Comparison Across AI Experts & Ensemble', fontsize=12, fontweight='bold', pad=12)
    plt.xticks(x_indices, models, rotation=15, ha='right', fontsize=10)
    plt.ylim([0, 105])  # Unclipped dynamic 0-100% scale
    plt.legend(loc='lower right')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    for i, v in enumerate(accuracies):
        plt.text(i - width/2, v + 1.2, f"{v:.1f}%", ha='center', fontsize=9, fontweight='bold')
    for i, v in enumerate(f1_scores):
        plt.text(i + width/2, v + 1.2, f"{v:.1f}%", ha='center', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "model_accuracy_comparison.png"), dpi=200)
    plt.close()

    # Plot 7: Precision & Recall Comparison
    recalls = [
        test_fuzzy_metrics['recall_macro']*100,
        test_gnb_metrics['recall_macro']*100,
        test_dt_metrics['recall_macro']*100,
        test_eq_metrics['recall_macro']*100,
        test_ens_metrics['recall_macro']*100
    ]
    precisions = [
        test_fuzzy_metrics['precision_macro']*100,
        test_gnb_metrics['precision_macro']*100,
        test_dt_metrics['precision_macro']*100,
        test_eq_metrics['precision_macro']*100,
        test_ens_metrics['precision_macro']*100
    ]

    plt.figure(figsize=(10, 6))
    plt.bar(x_indices - width/2, precisions, width, label='Macro Precision (%)', color='#3D8054')
    plt.bar(x_indices + width/2, recalls, width, label='Macro Recall (%)', color='#758279')
    plt.ylabel('Score (%)', fontsize=11, fontweight='bold')
    plt.title('Macro Precision & Recall Comparison Across AI Models (Test Set)', fontsize=12, fontweight='bold', pad=12)
    plt.xticks(x_indices, models, rotation=15, ha='right', fontsize=10)
    plt.ylim([0, 105])
    plt.legend(loc='lower right')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "model_precision_recall_comparison.png"), dpi=200)
    plt.close()

    # Plot 8: Ensemble Weights Distribution
    plt.figure(figsize=(7, 5))
    weight_labels = ['Fuzzy Logic (W1)', 'Gaussian NB (W2)', 'Decision Tree (W3)']
    weight_vals = [w1, w2, w3]
    colors = ['#E8AD45', '#174B35', '#3D8054']
    plt.pie(weight_vals, labels=weight_labels, autopct='%1.1f%%', colors=colors, startangle=140, explode=(0.04, 0.04, 0.04))
    plt.title(f'Optimized Hybrid Ensemble Weight Allocation (Simplex Optimization)\nFinalScore = {w1:.2f}·Fuzzy + {w2:.2f}·GNB + {w3:.2f}·DT', fontsize=11, fontweight='bold', pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "ensemble_weights_distribution.png"), dpi=200)
    plt.close()

    # Plot 9: Decision Tree Feature Importances (Gini & Permutation)
    dt_gini = dt_expert.get_feature_importances()
    dt_perm = dt_expert.get_permutation_importances(X_train, y_train)

    sorted_feats = sorted(FEATURE_NAMES, key=lambda f: dt_gini[f], reverse=True)
    gini_vals = [dt_gini[f] for f in sorted_feats]
    perm_vals = [dt_perm[f] for f in sorted_feats]

    plt.figure(figsize=(9, 5))
    y_pos = np.arange(len(sorted_feats))
    plt.barh(y_pos - 0.2, gini_vals, 0.4, label='Gini Impurity Decrease', color='#3D8054')
    plt.barh(y_pos + 0.2, perm_vals, 0.4, label='Permutation Accuracy Drop', color='#E8AD45')
    plt.yticks(y_pos, sorted_feats, fontsize=10)
    plt.xlabel('Statistical Importance Metric', fontsize=11, fontweight='bold')
    plt.title('Decision Tree Feature Importance Hierarchy (Non-Causal Diagnostic)', fontsize=11, fontweight='bold', pad=12)
    plt.gca().invert_yaxis()
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "decision_tree_feature_importance.png"), dpi=200)
    plt.close()

    # Save comprehensive evaluation report
    eval_report = {
        "dataset_metadata": {
            "name": "Crop Recommendation Dataset",
            "sha256": dataset_hash,
            "total_samples": len(X),
            "train_samples": len(X_train),
            "val_samples": len(X_val),
            "test_samples": len(X_test),
            "features": FEATURE_NAMES,
            "classes": classes,
            "classes_count": len(classes)
        },
        "hyperparameter_cross_validation": {
            "gaussian_nb": {
                "method": "5-Fold Stratified Cross-Validation on Training Split",
                "best_var_smoothing": gnb_cv_results["best_var_smoothing"],
                "cv_macro_f1": gnb_cv_results["best_cv_macro_f1"]
            },
            "decision_tree": {
                "method": "5-Fold Stratified Cross-Validation on Training Split",
                "best_params": dt_cv_results["best_params"],
                "effective_depth": dt_cv_results["effective_depth"],
                "cv_macro_f1": dt_cv_results["best_cv_macro_f1"]
            }
        },
        "validation_simplex_optimization": opt_report,
        "test_evaluation_untouched": {
            "fuzzy_logic": test_fuzzy_metrics,
            "gaussian_nb": test_gnb_metrics,
            "decision_tree": test_dt_metrics,
            "equal_weight_ensemble": test_eq_metrics,
            "optimized_hybrid_ensemble": test_ens_metrics
        },
        "ensemble_weights": {
            "fuzzy_logic": w1,
            "gaussian_nb": w2,
            "decision_tree": w3
        },
        "per_class_summary": clf_report
    }

    report_path = os.path.join(REPORTS_DIR, "model_evaluation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(to_json_serializable(eval_report), f, indent=2)
    print(f"\nSaved comprehensive evaluation report to {report_path}")

    # Save and validate artifacts via Model Registry
    registry = ModelRegistry()
    registry.save_models(
        fuzzy_expert=fuzzy_expert,
        gnb_expert=gnb_expert,
        dt_expert=dt_expert,
        ensemble=ensemble,
        metadata={
            "evaluation_metrics": eval_report["test_evaluation_untouched"],
            "hyperparameters": eval_report["hyperparameter_cross_validation"],
            "dataset_info": eval_report["dataset_metadata"]
        },
        version="v1.1"
    )

    print("\n🎉 PHASE 3.1: TRAINING PIPELINE EXECUTION COMPLETED SUCCESSFULLY! 🎉")
    return eval_report


if __name__ == "__main__":
    train_and_evaluate()
