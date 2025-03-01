#!/bin/bash
set -e

# Install uv if not already installed
if ! command -v uv &> /dev/null
then
    echo "uv could not be found, installing..."
    pip install uv
else
    echo "uv is already installed"
fi

echo "Creating virtual environment..."
uv venv

echo "Activiting virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
uv pip install -e packages/*

echo "Running test CLI command"
cli --help

echo "Setup Complete!"