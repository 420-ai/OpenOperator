# Use official NVIDIA CUDA image with Python 3.10 and cuDNN
FROM nvidia/cuda:12.6.0-cudnn-runtime-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="/root/.local/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    python3.10 \
    python3.10-venv \
    python3-pip \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install uv - fast Python package manager
RUN curl -Ls https://astral.sh/uv/install.sh | sh

# Verify uv
RUN which uv && uv --version

# Copy project files
COPY . .

# # Debug: show working directory and contents again
# RUN echo "Working directory:" && pwd
# RUN echo "Contents of current folder:" && ls -al .

# Create uv virtual environment and install dependencies
RUN uv venv
RUN uv sync

# Set entry point
CMD ["uv", "run", "server.py"]
