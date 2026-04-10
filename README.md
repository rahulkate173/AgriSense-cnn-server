# Plant Disease Classifier API

A FastAPI server that classifies plant diseases using a custom EfficientNet-B0 model and provides actionable advice using Groq AI.

## Project Structure
- `main.py`: FastAPI server with `/predict` route.
- `model_utils.py`: PyTorch inference logic.
- `ai_service.py`: Groq LLM integration.
- `config.py`: Configuration and class names.
- `Dockerfile`: Container setup using `uv`.
- `.github/workflows/`: CI/CD setup.

## Setup Instructions

### 1. Model Weights
Place your `best_efficientnet.pth` file in the root directory of this project.

### 2. Environment Variables
Create a `.env` file in the root directory and add your Groq API key:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Local Development
We recommend using [uv](https://github.com/astral-sh/uv) for fast package management.

```bash
# Install dependencies
uv sync

# Run the server
uv run uvicorn main:app --reload
```

### 4. API Endpoints
- **GET /**: Health check.
- **POST /predict**: Upload an image (JPEG/PNG) to get classification and AI feedback.
  - Returns: `{"class_label": "...", "confidence": 0.99, "response": "AI explanation..."}`

## Deployment on Render
1. Connect your GitHub repository to Render.
2. Select **Web Service**.
3. Render will detect the `Dockerfile`.
4. Add your `GROQ_API_KEY` in the Render environment variables dashboard.
5. **Important**: Since the model file (`.pth`) is large, ensure it is either committed to Git (using LFS if needed) or uploaded to a cloud storage and downloaded during build.
