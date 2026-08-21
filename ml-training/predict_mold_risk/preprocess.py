import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from supabase import create_client, Client

# 1. Point to .env in the parent folder (ml-training/.env)
SCRIPT_DIR = Path(__file__).resolve().parent          # predict_disease_risk/
PARENT_ML_DIR = SCRIPT_DIR.parent                     # ml-training/

load_dotenv(dotenv_path=PARENT_ML_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(f"Missing SUPABASE_URL or SUPABASE_KEY in {PARENT_ML_DIR}/.env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def calculate_risk_level(row):
    """
    Biological Rule-Based Labeling for Ground Truth (24h Window):
    - High Risk (2): High humidity (>=80%) for >= 50% of the last 24h (>= 12h total)
                     during optimal warm temperatures (18°C - 30°C). Spores germinating.
    - Medium Risk (1): High humidity for >= 25% of the last 24h (>= 6h total) 
                       OR average relative humidity >= 70%. Spores swelling.
    - Low Risk (0): Foliage dry, insufficient humidity for fungal spore germination.
    """
    ratio = row['high_humidity_ratio']
    avg_temp = row['avg_temp']
    avg_hum = row['avg_humidity']

    if ratio >= 0.50 and (18.0 <= avg_temp <= 30.0):
        return 2  # High
    elif ratio >= 0.25 or avg_hum >= 70.0:
        return 1  # Medium
    else:
        return 0  # Low

def preprocess():
    print("Fetching raw telemetry from Supabase...")
    
    # Query all columns from public.telemetry table
    response = supabase.table("telemetry") \
        .select("created_at, temperature, humidity, ambient_light, soil_moisture") \
        .order("created_at", desc=False) \
        .execute()
    
    data = response.data
    if not data:
        print("⚠️ No telemetry data found in database.")
        return

    df = pd.DataFrame(data)
    print(f"Total raw rows fetched from DB: {len(df)}")

    # 2. Convert created_at to DatetimeIndex for time-based rolling calculations
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values('created_at').set_index('created_at')

    # Flag individual readings with high humidity (1.0 = High, 0.0 = Normal)
    df['is_high_humidity'] = (df['humidity'] >= 80.0).astype(float)

    # 3. Apply 24-Hour Rolling Time Window ('24h') for all columns
    TIME_WINDOW = '24h'
    
    df['avg_temp'] = df['temperature'].rolling(TIME_WINDOW, min_periods=1).mean()
    df['avg_humidity'] = df['humidity'].rolling(TIME_WINDOW, min_periods=1).mean()
    df['avg_ambient_light'] = df['ambient_light'].rolling(TIME_WINDOW, min_periods=1).mean()
    df['avg_soil_moisture'] = df['soil_moisture'].rolling(TIME_WINDOW, min_periods=1).mean()
    df['high_humidity_ratio'] = df['is_high_humidity'].rolling(TIME_WINDOW, min_periods=1).mean()

    # 4. Generate Disease Risk Ground Truth Target
    df['disease_risk_level'] = df.apply(calculate_risk_level, axis=1)

    feature_cols = ['avg_temp', 'avg_humidity', 'avg_ambient_light', 'avg_soil_moisture', 'high_humidity_ratio']

    # 5. Clean & Filter out NaNs AND any rows where any of the feature columns equals 0
    clean_df = df.dropna(subset=feature_cols).copy()
    
    # Filter out rows where any feature is 0
    clean_df = clean_df[(clean_df[feature_cols] != 0).all(axis=1)].copy()
    
    print(f"Rows remaining after cleaning NaNs and zero-value features: {len(clean_df)}")

    final_df = clean_df[[
        'avg_temp', 
        'avg_humidity', 
        'avg_ambient_light', 
        'avg_soil_moisture', 
        'high_humidity_ratio', 
        'disease_risk_level'
    ]]

    # 6. Export dataset to current use-case directory
    output_path = SCRIPT_DIR / "dataset.csv"
    final_df.to_csv(output_path, index=False)
    print(f"✅ Preprocessing complete! Exported dataset to: {output_path}")

if __name__ == "__main__":
    preprocess()