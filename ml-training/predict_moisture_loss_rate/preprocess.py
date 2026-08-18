import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from supabase import create_client, Client

# 1. Point to .env in the parent folder (ml-training/.env)
SCRIPT_DIR = Path(__file__).resolve().parent          # predict_moisture_loss_rate/
PARENT_ML_DIR = SCRIPT_DIR.parent                     # ml-training/

load_dotenv(dotenv_path=PARENT_ML_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(f"Missing SUPABASE_URL or SUPABASE_KEY in {PARENT_ML_DIR}/.env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def preprocess():
    print("Fetching raw telemetry from Supabase...")
    
    response = supabase.table("telemetry") \
        .select("created_at, temperature, humidity, ambient_light, soil_moisture") \
        .order("created_at", desc=False) \
        .execute()
    
    data = response.data
    if not data:
        print("⚠️ No telemetry data found in database.")
        return

    df = pd.DataFrame(data)

    # 2. Clean & Calculate Moisture Decay Rate (% drop per hour)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['time_diff_hours'] = df['created_at'].diff().dt.total_seconds() / 3600.0
    df['moisture_drop'] = -df['soil_moisture'].diff()
    df['decay_rate'] = df['moisture_drop'] / df['time_diff_hours']

    # 3. Filter out noise
    # Print raw count for debugging
    print(f"Total raw rows fetched from DB: {len(df)}")

    # 1. Allow zero or small drops, adjust outlier ceiling
    clean_df = df[
        (df['decay_rate'] >= 0) &      # Changed from > 0 to >= 0
        # (df['decay_rate'] < 100) &     # Increased upper threshold for 10-sec samples
        (df['time_diff_hours'] > 0)
    ].copy()

    print(f"Rows remaining after filtering: {len(clean_df)}")

    final_df = clean_df[[
        'temperature', 
        'humidity', 
        'ambient_light', 
        'soil_moisture', 
        'decay_rate'
    ]]

    # 4. Save dataset in the current use-case folder
    output_path = SCRIPT_DIR / "dataset.csv"
    final_df.to_csv(output_path, index=False)
    print(f"✅ Preprocessing complete! Exported dataset to: {output_path}")

if __name__ == "__main__":
    preprocess()