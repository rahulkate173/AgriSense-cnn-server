from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from model_utils import load_model, predict_image, fetch_image_from_url
from config import MODEL_VERSIONS, DEFAULT_VERSION
from ai_service import get_ai_feedback
from typing import Dict, Any
from pydantic import BaseModel
import os 
# Request model for ImageKit URLs
class ImageRequest(BaseModel):
    image_url: str = Query(..., description="ImageKit URL of the image to classify")
    version: str = Query(DEFAULT_VERSION, description="Model version to use")

app = FastAPI(
    title="Plant Disease Classifier API",
    description="Classifies plant diseases using CNN, taking ImageKit URLs as input and providing AI feedback via Groq.",
    version="1.0.0"
)

# Enable CORS for local testing and deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global models dictionary to be loaded on startup
loaded_models = {}
@app.on_event("startup")
async def startup_event():
    global loaded_models
    print("=== STARTUP: Loading models ===")

    for version, config in MODEL_VERSIONS.items():
        path = config["path"]
        print(f"Loading model {version} from {path}")
        m = load_model(path, config["type"])
        if m is not None:
            loaded_models[version] = m
            print(f"✅ Model {version} loaded")
        else:
            print(f"❌ Model {version} NOT loaded (file not found or failed to load)")
    
    print("=== loaded_models =", loaded_models)

@app.get("/")
async def root():
    return {"message": "Plant Disease Classifier API is running", "loaded_versions": list(loaded_models.keys())}

@app.post("/predict")
async def predict(
    image_url: str = Query(..., description="ImageKit URL of the image"),
    version: str = Query(DEFAULT_VERSION, description="Model version to use (e.g., 'latest', 'v1', 'v2')")
) -> Dict[str, Any]:
    """
    Accepts ImageKit URLs for plant disease classification.
    Returns prediction with multilingual response (English, Hindi, Marathi).
    """
    try:
        # Check if requested model version is loaded
        if version not in loaded_models:
            raise HTTPException(status_code=400, detail=f"Model version '{version}' not found. Available versions: {list(loaded_models.keys())}")
        
        selected_model = loaded_models[version]
        
        # Fetch image from ImageKit URL
        image_content = fetch_image_from_url(image_url)
        
        # 1. Get Model Prediction
        class_label, confidence = predict_image(selected_model, image_content)
        
        # 2. Get AI Feedback from Groq (with multilingual response)
        ai_response = get_ai_feedback(class_label, confidence)
        
        # Return as JSON with structured response
        return {
            "class_label": class_label,
            "confidence": float(confidence),
            "response": ai_response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

if __name__ == "__main__":
    # This reads the PORT env var, or defaults to 8000 if it's missing
    uvicorn.run("main:app", host="0.0.0.0", port=800)