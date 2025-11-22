#!/bin/bash
cd "$(dirname "$0")"

# Start the backend server
uv run uvicorn app:app --reload --port 8000
