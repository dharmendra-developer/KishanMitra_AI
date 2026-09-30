"""
KisanMitra AI model adapter.
Demo fallback is used until a trained model is placed at models/crop_disease.keras.
"""
from pathlib import Path

def predict(image_path):
    model_path=Path(__file__).parent/"models"/"crop_disease.keras"
    if not model_path.exists():
        return {"crop":"Tomato","disease":"Early Blight","confidence":0.86}
    # Plug your TensorFlow/Keras preprocessing + model.predict() here.
    raise NotImplementedError("Add model-specific preprocessing and class labels.")
