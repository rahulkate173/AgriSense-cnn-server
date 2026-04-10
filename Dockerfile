# Use a Python base image
FROM python:3.10-slim

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project files
COPY pyproject.toml .
# If you have a lockfile, uncomment the next line
# COPY uv.lock .

# Install dependencies using uv
RUN uv sync --frozen --no-cache

# Copy the rest of the application
COPY . .

# Expose the port (Render uses $PORT environment variable)
EXPOSE 8000

# Start the application
# We use 'uv run' to ensure we're using the virtual environment managed by uv
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
