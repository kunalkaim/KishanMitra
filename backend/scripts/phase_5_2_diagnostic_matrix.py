import sys
import os
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ml.crop_recommendation.predictor import CropRecommendationPredictor
from app.ml.crop_recommendation.ensemble import HybridWeightedCropEnsemble

# Load raw dataset to get empirical feature centers for each crop
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../datasets/crop_recommendation/raw/Crop_recommendation.csv'))
df = pd.read_csv(DATA_PATH)

predictor = CropRecommendationPredictor.get_instance()
ensemble = predictor.ensemble
explainer = predictor.explainer
classes = ensemble.classes_

print(f"Total dataset rows: {len(df)}")
print(f"Total classes: {len(classes)}")
print(f"Ensemble weights: {ensemble.weights}")

# Compute crop centers (median of each feature per crop)
crop_profiles = df.groupby('label')[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']].median()

results = []

print("\n" + "="*80)
print(f"{'Crop Target':<15} | {'Top-1 Predicted':<15} | {'Score':<6} | {'Match?':<6} | {'Top-3 Predictions'}")
print("="*80)

match_count = 0
for crop_name in classes:
    median_feats = crop_profiles.loc[crop_name].to_dict()
    
    # 1. Component scores
    df_single = pd.DataFrame([median_feats])
    fuzzy_scores, gnb_probs, dt_probs = ensemble.predict_component_scores(df_single)
    fuzzy_s = fuzzy_scores[0]
    gnb_p = gnb_probs[0]
    dt_p = dt_probs[0]
    
    # 2. Ensemble score
    w1, w2, w3 = ensemble.weights
    ens_scores = (w1 * fuzzy_s) + (w2 * gnb_p) + (w3 * dt_p)
    ens_scores = ens_scores / np.sum(ens_scores)
    
    # 3. Top-3
    ranked_indices = np.argsort(ens_scores)[::-1]
    top_3 = [classes[idx] for idx in ranked_indices[:3]]
    top_1 = top_3[0]
    top_1_score = ens_scores[ranked_indices[0]] * 100.0
    
    is_match = (top_1 == crop_name)
    if is_match:
        match_count += 1
        
    print(f"{crop_name:<15} | {top_1:<15} | {top_1_score:5.1f}% | {str(is_match):<6} | {', '.join(top_3)}")
    
    results.append({
        "target_crop": crop_name,
        "input_features": median_feats,
        "fuzzy_top1": classes[int(np.argmax(fuzzy_s))],
        "fuzzy_score_for_target": float(fuzzy_s[classes.index(crop_name)]),
        "fuzzy_score_for_rice": float(fuzzy_s[classes.index('rice')]),
        "gnb_top1": classes[int(np.argmax(gnb_p))],
        "gnb_prob_for_target": float(gnb_p[classes.index(crop_name)]),
        "gnb_prob_for_rice": float(gnb_p[classes.index('rice')]),
        "dt_top1": classes[int(np.argmax(dt_p))],
        "dt_prob_for_target": float(dt_p[classes.index(crop_name)]),
        "dt_prob_for_rice": float(dt_p[classes.index('rice')]),
        "ensemble_top1": top_1,
        "ensemble_top3": top_3,
        "ensemble_score_for_target": float(ens_scores[classes.index(crop_name)]),
        "ensemble_score_for_rice": float(ens_scores[classes.index('rice')])
    })

print("="*80)
print(f"Accuracy on Crop Median Centroids: {match_count}/{len(classes)} ({match_count/len(classes)*100:.1f}%)")
