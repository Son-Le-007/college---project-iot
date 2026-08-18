import os
from pathlib import Path
import pandas as pd
import joblib  # Standard for scikit-learn models (or keep 'import pickle')

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "ml-artifacts" / "predict_moisture_loss_rate" / "model.pkl"

_model = None

def load_model():
    global _model
    if _model is not None:
        return _model
    
    if not MODEL_PATH.exists():
        print(f"⚠️ [AI Inference] Model artifact not found at: {MODEL_PATH}")
        return None
    
    try:
        # joblib handles scikit-learn model unpickling smoothly
        _model = joblib.load(MODEL_PATH)
        print("✅ [AI Inference] Model loaded successfully.")
        return _model
    except Exception as e:
        print(f"❌ [AI Inference] Failed to load model: {str(e)}")
        return None

def predict_moisture_loss_rate(
    temperature: float, 
    humidity: float, 
    soil_moisture: float, 
    ambient_light: float
) -> float:
    model = load_model()
    if model is None:
        return 0.0
    
    try:
        # Match exact feature order used during training:
        # ['temperature', 'humidity', 'ambient_light', 'soil_moisture']
        input_data = pd.DataFrame([{
            "temperature": temperature,
            "humidity": humidity,
            "ambient_light": ambient_light,
            "soil_moisture": soil_moisture
        }])
        
        prediction = model.predict(input_data)
        
        # Ensure predicted decay rate is non-negative
        predicted_rate = float(prediction[0])
        return max(0.0, predicted_rate)
        
    except Exception as e:
        print(f"❌ [AI Inference] Prediction failed: {str(e)}")
        return 0.0