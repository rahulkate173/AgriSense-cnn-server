# Use a Python base image
FROM python:3.10-slim

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# ENV UV_PYTHON_PREFERENCE=only-binary   # ← remove this line

# Copy project files
COPY pyproject.toml uv.lock .

# Install dependencies using uv with CPU-only torch
RUN uv sync --frozen --no-cache --python 3.10 && \
    . .venv/bin/activate && \
    pip install --no-cache-dir --upgrade torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 8000

# Start the application
#CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]
CMD ["uv", "run", "python", "main.py"]