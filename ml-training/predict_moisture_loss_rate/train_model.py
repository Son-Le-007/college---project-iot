from pathlib import Path
import pandas as pd
from sklearn.linear_model import LinearRegression
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
    X = df[['temperature', 'humidity', 'ambient_light', 'soil_moisture']]
    y = df['decay_rate']

    # 3. Train Model
    print("Training Linear Regression model...")
    model = LinearRegression()
    model.fit(X, y)

    # 4. Save model artifact
    joblib.dump(model, MODEL_PATH)
    print(f"✅ Training complete! Saved trained model artifact to: {MODEL_PATH}")

if __name__ == "__main__":
    train_and_export()