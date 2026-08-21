from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. Resolve paths dynamically relative to this script's location
SCRIPT_DIR = Path(__file__).resolve().parent
DATASET_PATH = SCRIPT_DIR / "dataset.csv"
MODEL_PATH = SCRIPT_DIR / "model.pkl"

def train_and_export():
    # Check if preprocessed CSV exists
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"❌ Dataset not found at {DATASET_PATH}. Please run preprocess.py first!"
        )

    print(f"Reading dataset from {DATASET_PATH}...")
    df = pd.read_csv(DATASET_PATH)

    if df.empty:
        raise ValueError("❌ Dataset CSV is empty. Cannot train model!")

    # 2. Separate Features (X) and Target (y)
    feature_cols = [
        'avg_temp', 
        'avg_humidity', 
        'avg_ambient_light', 
        'avg_soil_moisture', 
        'high_humidity_ratio'
    ]
    
    X = df[feature_cols]
    y = df['disease_risk_level']

    # 3. Train Model
    print("Training Random Forest Classifier model...")
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)

    # 4. Save model artifact
    joblib.dump(model, MODEL_PATH)
    print(f"✅ Training complete! Saved trained model artifact to: {MODEL_PATH}")

if __name__ == "__main__":
    train_and_export()