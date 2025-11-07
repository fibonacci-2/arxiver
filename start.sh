#!/bin/bash

echo "Starting Paper Producer Web UI..."
echo "Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

echo "Starting server..."
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
