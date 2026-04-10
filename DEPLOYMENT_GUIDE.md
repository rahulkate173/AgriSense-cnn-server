# FastAPI Deployment Guide - ImageKit Integration

## Summary of Changes Made ✅

Your API now:
- ✅ Accepts ImageKit URLs (not file uploads)
- ✅ Returns JSON with multilingual response (English, Hindi, Marathi)
- ✅ Fetches images directly from ImageKit
- ✅ Production-ready for Render deployment

## Response Format

The API now returns:
```json
{
  "class_label": "Tomato_Early_blight",
  "confidence": 0.95,
  "response": {
    "english": "Early blight is a fungal disease...",
    "hindi": "अर्ली ब्लाइट एक कवक रोग है...",
    "marathi": "आर्ली ब्लाइट एक बीजाणु रोग आहे..."
  }
}
```

## Example API Call

```bash
curl "http://localhost:8000/predict?image_url=https://ik.imagekit.io/bvwmtjesc/agrisense/marketplace/crop_1775759014940_tJL6WnEMn.png&version=latest"
```

---

## Models: What to Deploy vs GitHub

### ❌ DO NOT Deploy/Push to GitHub (too large):
- `checkpoint_epoch_5.pth`
- `checkpoint_epoch_10.pth`
- `checkpoint_epoch_15.pth`
- `checkpoint_epoch_20.pth`
- `checkpoint_epoch_25.pth`
- `checkpoint_epoch_30.pth`
- `checkpoint_epoch_35.pth`
- `checkpoint_epoch_40.pth`

### ✅ DO Deploy & Push to GitHub:
- **`best_model.pth`** (29 MB) - Your production model

**Why:** 
- Checkpoints are for training reference only
- Only `best_model.pth` is needed for inference
- GitHub has size limits; use `.gitignore` for checkpoints

### Add to `.gitignore`:
```gitignore
models/checkpoint_*.pth
# Keep only best_model.pth
!models/best_model.pth
```

---

## Render Deployment Steps

### 1. **Model Storage on Render**

**Option A: Build Context (Recommended for ~29 MB)**
- Add `models/best_model.pth` to GitHub
- Render will download it during build

**Option B: Large Files Storage**
- Use Render's Disks feature if model > 100 MB
- SSH into your service and upload model to persistent disk

**Directory structure in production:**
```
/opt/render/project  (or your project root)
└── models/
    └── best_model.pth
```

### 2. **Update config.py for Production**

Ensure path is relative to project root:
```python
MODEL_VERSIONS = {
    "latest": {"path": "models/best_model.pth", "type": "plantcnn"}
}
```

### 3. **Environment Variables on Render**

In Render dashboard → Environment → Add:
- `GROQ_API_KEY`: Your Groq API key
- `PYTHON_VERSION`: (optional) 3.11 or 3.12

### 4. **Build Command**
```bash
pip install -r requirements.txt -e .
```

Or if using `pyproject.toml`:
```bash
pip install .
```

### 5. **Start Command**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 6. **Resource Allocation**
- **RAM**: 2-4 GB (sufficient for best_model.pth)
- **CPU**: Standard-1X should work

---

## Testing ImageKit Integration

### Local Testing:
```bash
curl -X GET "http://localhost:8000/predict?image_url=YOUR_IMAGEKIT_URL&version=latest"
```

### Example with Real ImageKit URL:
```bash
curl -X GET "http://localhost:8000/predict?image_url=https://ik.imagekit.io/bvwmtjesc/agrisense/marketplace/crop_1775759014940_tJL6WnEMn.png&version=latest"
```

---

## Integration with Node.js Backend

Your Node.js app can now call this API:

```javascript
// Node.js backend
const imagekitUrl = "https://ik.imagekit.io/bvwmtjesc/agrisense/marketplace/crop_1775759014940_tJL6WnEMn.png";

const response = await fetch(
  `https://your-fastapi-service.onrender.com/predict?image_url=${encodeURIComponent(imagekitUrl)}&version=latest`
);

const result = await response.json();
console.log(result);
// Output: { class_label, confidence, response: { english, hindi, marathi } }
```

---

## Files Modified

| File | Changes |
|------|---------|
| `main.py` | Changed from file upload to ImageKit URL input |
| `ai_service.py` | Returns structured multilingual JSON response |
| `model_utils.py` | Added `fetch_image_from_url()` function + `requests` import |
| `pyproject.toml` | Added `requests` dependency |

---

## Troubleshooting

### Model not found on Render
- Ensure `best_model.pth` is in GitHub repo
- Check if paths in config.py are relative

### ImageKit URL fetch fails
- Verify URL is publicly accessible
- Check ImageKit permissions
- Add request timeout handling (already in code)

### Memory issues
- Use Render's Disk feature for model storage
- Consider model quantization if > 100 MB

---

## API Endpoints

### GET `/`
Returns API status and loaded model versions.

### POST `/predict`
**Parameters:**
- `image_url` (string, required): ImageKit URL
- `version` (string, optional): Model version, default="latest"

**Response:**
```json
{
  "class_label": "string",
  "confidence": "float (0-1)",
  "response": {
    "english": "string",
    "hindi": "string",
    "marathi": "string"
  }
}
```

**Error handling:**
- Returns HTTP 400 if model version not found
- Returns HTTP 500 if image fetch/prediction fails
