import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile" # High quality model available on Groq

# Model Configuration
MODEL_VERSIONS = {
    "v1": {"path": "best_efficientnet.pth", "type": "efficientnet"},
    "v2": {"path": "models/best_model.pth", "type": "plantcnn"},
    "latest": {"path": "models/best_model.pth", "type": "plantcnn"}
}
DEFAULT_VERSION = "latest"
NUM_CLASSES = 15

# Ordered class names based on the provided dictionary
CLASS_NAMES = [
    "Pepper__bell___Bacterial_spot",
    "Pepper__bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato_Bacterial_spot",
    "Tomato_Early_blight",
    "Tomato_Late_blight",
    "Tomato_Leaf_Mold",
    "Tomato_Septoria_leaf_spot",
    "Tomato_Spider_mites_Two-spotted_spider_mite",
    "Tomato_Target_Spot",
    "Tomato_Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato_Tomato_mosaic_virus",
    "Tomato_healthy"
]
