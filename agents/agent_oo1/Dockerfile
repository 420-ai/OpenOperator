# Use an official Python base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install uv - fast Python package manager
RUN curl -Ls https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

# Verify uv
RUN which uv && uv --version

# ------------------------------
RUN echo "Working directory:" && pwd
RUN echo "Contents of current folder:" && ls -al .
# ------------------------------

# Copy project files
COPY ./agent_oo1/ ./agent_oo1/

# Copy local dependencies
COPY ./core/ ./core/
COPY ./functions/ ./functions/

# Copy configs
COPY ./configs/ ./configs/

# ------------------------------
RUN echo "Working directory:" && pwd
RUN echo "Contents of current folder:" && ls -al .
# ------------------------------

WORKDIR /app/agent_oo1

# ------------------------------
RUN echo "Working directory:" && pwd
RUN echo "Contents of current folder:" && ls -al .
# ------------------------------

# Create uv virtual environment
RUN uv venv
RUN echo "---A---"

# Install dependencies using uv sync
RUN uv sync
RUN echo "---B---"

# WORKDIR /app

ENV PYTHONPATH=/app

# ------------------------------
RUN echo "Working directory:" && pwd
RUN echo "Contents of current folder:" && ls -al .
# ------------------------------

# Set entry point
CMD ["uv", "run", "-m", "main"]
