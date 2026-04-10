import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import io
import requests
from config import CLASS_NAMES, MODEL_VERSIONS, NUM_CLASSES

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class PlantCNN(nn.Module):
    def __init__(self, num_classes):
        super(PlantCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.conv3 = nn.Conv2d(64, 64, 3, padding=1)
        self.conv4 = nn.Conv2d(64, 64, 3, padding=1)
        self.conv5 = nn.Conv2d(64, 64, 3, padding=1)
        self.conv6 = nn.Conv2d(64, 64, 3, padding=1)
        self.conv7 = nn.Conv2d(64, 64, 3, padding=1)
        self.fc1 = nn.Linear(64 * 3 * 3, 64)
        self.fc2 = nn.Linear(64, num_classes)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        # 224x224x3
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = self.pool(F.relu(self.conv4(x)))
        x = self.pool(F.relu(self.conv5(x)))
        x = F.relu(self.conv6(x))
        x = self.pool(F.relu(self.conv7(x)))
        x = x.view(-1, 64 * 3 * 3)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

# Standard ImageNet transforms for EfficientNet
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def load_model(model_path, model_type):
    """Loads the model from the specified checkpoint path based on its architecture type."""
    model = PlantCNN(NUM_CLASSES)
        
    try:
        checkpoint = torch.load(model_path, map_location=device)
        # Handle cases where checkpoint might be just the state dict or a dictionary
        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            model.load_state_dict(checkpoint["model_state_dict"])
        else:
            model.load_state_dict(checkpoint)
        
        model = model.to(device)
        model.eval()
        print(f"Model ({model_type}) loaded successfully from {model_path}")
        return model
    except FileNotFoundError:
        print(f"Warning: model file not found at {model_path}.")
        return None
    except Exception as e:
        print(f"Error loading model from {model_path}: {e}")
        return None

@torch.no_grad()
def predict_image(model, image_bytes):
    """Predicts the class of an image provided as bytes."""
    if model is None:
        raise ValueError("Model is not loaded.")

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_tensor = transform(image).unsqueeze(0).to(device)

    outputs = model(image_tensor)
    probs = torch.softmax(outputs, dim=1)
    pred_idx = torch.argmax(probs, dim=1).item()
    confidence = probs[0, pred_idx].item()

    return CLASS_NAMES[pred_idx], confidence

def fetch_image_from_url(image_url: str):
    """Fetches image from ImageKit URL and returns as bytes."""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch image from URL: {str(e)}")
