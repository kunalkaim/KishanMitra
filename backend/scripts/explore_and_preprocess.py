import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

RAW_DATA_PATH = os.path.join("datasets", "crop_recommendation", "raw", "Crop_recommendation.csv")
PROCESSED_DATA_PATH = os.path.join("datasets", "crop_recommendation", "processed", "cleaned_crop_recommendation.csv")
REPORTS_DIR = os.path.join("datasets", "crop_recommendation", "reports")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")

os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

def explore_and_preprocess():
    print(f"Loading raw dataset from {RAW_DATA_PATH}...")
    df = pd.read_csv(RAW_DATA_PATH)
    
    # 1. Schema & basic metrics
    total_records, total_columns = df.shape
    columns = list(df.columns)
    
    # Normalize column names: strip whitespace
    df.columns = [c.strip() for c in df.columns]
    feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    target_col = 'label'
    
    # 2. Check missing values
    missing_counts = df.isnull().sum().to_dict()
    total_missing = int(df.isnull().sum().sum())
    
    # 3. Check duplicate rows
    duplicate_count = int(df.duplicated().sum())
    
    # 4. Target class analysis
    class_counts = df[target_col].value_counts().to_dict()
    unique_crops = sorted(list(df[target_col].unique()))
    num_classes = len(unique_crops)
    is_balanced = len(set(class_counts.values())) == 1
    samples_per_class = int(list(class_counts.values())[0]) if is_balanced else "variable"
    
    # 5. Numerical ranges and summary stats
    desc = df[feature_cols].describe().T
    desc['skew'] = df[feature_cols].skew()
    desc['kurtosis'] = df[feature_cols].kurtosis()
    desc_dict = desc.to_dict(orient='index')
    
    # Outlier detection via IQR
    outlier_info = {}
    for col in feature_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        outlier_info[col] = {
            "q1": float(q1),
            "q3": float(q3),
            "iqr": float(iqr),
            "lower_bound": float(lower_bound),
            "upper_bound": float(upper_bound),
            "outlier_count": int(len(outliers)),
            "outlier_percentage": round(float(len(outliers) / total_records * 100), 2)
        }
    
    # 6. Save dataset summary CSV
    desc.to_csv(os.path.join(REPORTS_DIR, "dataset_summary.csv"))
    print("Saved dataset_summary.csv")
    
    # 7. Save cleaned/processed CSV (preserving intact raw values, verified types)
    # Cast types properly
    for col in ['N', 'P', 'K']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    for col in ['temperature', 'humidity', 'ph', 'rainfall']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df[target_col] = df[target_col].astype(str).str.strip().str.lower()
    
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"Saved cleaned dataset to {PROCESSED_DATA_PATH}")
    
    # 8. Save Data Quality Report JSON
    quality_report = {
        "dataset_name": "Crop Recommendation Dataset",
        "file_path": RAW_DATA_PATH,
        "processed_file_path": PROCESSED_DATA_PATH,
        "total_records": total_records,
        "total_columns": total_columns,
        "features": feature_cols,
        "target": target_col,
        "unique_classes_count": num_classes,
        "unique_crops": unique_crops,
        "is_perfectly_balanced": is_balanced,
        "samples_per_class": samples_per_class,
        "missing_values": missing_counts,
        "total_missing_values": total_missing,
        "duplicate_records": duplicate_count,
        "outlier_analysis_iqr": outlier_info,
        "agronomic_outlier_treatment_policy": (
            "No records removed. Agricultural feature distributions reflect true biological specializations "
            "(e.g., rice requires extreme rainfall >200mm, whereas chickpea/kidney beans require low rainfall; "
            "apple requires low temperatures and high potassium). Discarding statistical outliers would destroy "
            "the distinguishing environmental niche of specialized crop varieties."
        ),
        "feature_summary_statistics": desc_dict
    }
    
    with open(os.path.join(REPORTS_DIR, "dataset_quality_report.json"), "w", encoding="utf-8") as f:
        json.dump(quality_report, f, indent=2)
    print("Saved dataset_quality_report.json")
    
    # 9. Visualizations
    print("Generating comprehensive exploratory figures...")
    sns.set_theme(style="whitegrid", palette="muted")
    
    # Figure 1: Class Distribution
    plt.figure(figsize=(12, 6))
    sns.countplot(data=df, x='label', order=df['label'].value_counts().index, color='#174B35')
    plt.title("Figure 1: Crop Class Sample Distribution (N=2200, 22 Classes)", fontsize=14, fontweight='bold', pad=12)
    plt.xlabel("Crop Category", fontsize=11, fontweight='bold')
    plt.ylabel("Sample Count", fontsize=11, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "01_crop_class_distribution.png"), dpi=200)
    plt.close()
    
    # Figures 2-8: Individual Feature Distributions (Hist + KDE)
    feature_meta = [
        ('N', 'Nitrogen (N) Content (kg/ha)', '#2E7D32', '02_nitrogen_distribution.png', 'Figure 2'),
        ('P', 'Phosphorus (P) Content (kg/ha)', '#1565C0', '03_phosphorus_distribution.png', 'Figure 3'),
        ('K', 'Potassium (K) Content (kg/ha)', '#6A1B9A', '04_potassium_distribution.png', 'Figure 4'),
        ('temperature', 'Ambient Temperature (°C)', '#D84315', '05_temperature_distribution.png', 'Figure 5'),
        ('humidity', 'Relative Humidity (%)', '#00838F', '06_humidity_distribution.png', 'Figure 6'),
        ('ph', 'Soil pH Level', '#4E342E', '07_soil_ph_distribution.png', 'Figure 7'),
        ('rainfall', 'Annual / Seasonal Rainfall (mm)', '#0277BD', '08_rainfall_distribution.png', 'Figure 8'),
    ]
    
    for col, title, color, fname, fig_num in feature_meta:
        plt.figure(figsize=(8, 5))
        sns.histplot(df[col], kde=True, color=color, bins=30, stat="density", alpha=0.6)
        plt.title(f"{fig_num}: Distribution of {title}", fontsize=13, fontweight='bold', pad=10)
        plt.xlabel(title, fontsize=11, fontweight='bold')
        plt.ylabel("Density", fontsize=11, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, fname), dpi=200)
        plt.close()
        
    # Figure 9: Correlation Heatmap
    plt.figure(figsize=(9, 7))
    corr = df[feature_cols].corr()
    sns.heatmap(corr, annot=True, cmap="YlGnBu", fmt=".2f", linewidths=0.5, cbar_kws={'label': 'Pearson Correlation'})
    plt.title("Figure 9: Soil Nutrient & Agro-Climatic Feature Correlation Heatmap", fontsize=13, fontweight='bold', pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "09_correlation_heatmap.png"), dpi=200)
    plt.close()
    
    # Figure 10: Soil N-P-K and Rainfall vs Top Classes (Grouped Boxplot)
    plt.figure(figsize=(16, 8))
    key_crops = ['rice', 'wheat', 'chickpea', 'kidneybeans', 'blackgram', 'apple', 'mungbean', 'maize', 'cotton', 'coffee']
    subset = df[df['label'].isin(key_crops)]
    sns.boxplot(data=subset, x='label', y='rainfall', palette="Set2")
    plt.title("Figure 10: Rainfall Affinity Across Representative Crop Varieties", fontsize=14, fontweight='bold', pad=12)
    plt.xlabel("Crop Variety", fontsize=12, fontweight='bold')
    plt.ylabel("Rainfall Requirement (mm)", fontsize=12, fontweight='bold')
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "10_crop_rainfall_relationships.png"), dpi=200)
    plt.close()

    print("All 10 figures and quality reports generated successfully!")
    print(f"Summary: {total_records} rows, {num_classes} classes, {total_missing} missing, {duplicate_count} duplicates.")

if __name__ == "__main__":
    explore_and_preprocess()
