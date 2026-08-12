import os
import joblib
import pandas as pd
from typing import Dict, List, Tuple
from app.ml.preprocess import clean_dataframe

# Global cache for the loaded model artifact
_MODEL_ARTIFACT = None
MODEL_PATH = "models/career_model.joblib"

def load_model():
    """
    Loads and caches the serialized model artifact.
    """
    global _MODEL_ARTIFACT
    if _MODEL_ARTIFACT is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model file not found at '{MODEL_PATH}'. "
                f"Please ensure the ML model is trained and saved before running inference."
            )
        _MODEL_ARTIFACT = joblib.load(MODEL_PATH)
    return _MODEL_ARTIFACT

def predict_careers(profile: Dict, top_n: int = 5) -> List[Tuple[str, float]]:
    """
    Runs model inference on a raw user profile dict.
    Returns a list of tuples: (career_role, match_probability_percentage)
    sorted in descending order of probability.
    """
    model_artifact = load_model()
    pipeline = model_artifact["pipeline"]
    
    # Convert profile dict to DataFrame
    df = pd.DataFrame([profile])
    
    # Clean dataframe using same function as training
    df_cleaned = clean_dataframe(df)
    
    # Get probability predictions
    probabilities = pipeline.predict_proba(df_cleaned)[0]
    classes = pipeline.classes_
    
    # Pair class names with their probability
    class_probs = list(zip(classes, probabilities))
    
    # Sort by probability descending
    class_probs.sort(key=lambda x: x[1], reverse=True)
    
    # Convert probability to percentage (0 - 100)
    recommendations = [
        (career, float(prob * 100))
        for career, prob in class_probs[:top_n]
    ]
    
    return recommendations
