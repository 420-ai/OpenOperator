FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv venv && \
    . .venv/bin/activate && \
    uv sync

# Copy the application code
COPY main.py ./
COPY test_connection.py ./

# Run the script
CMD [".venv/bin/python", "main.py"]