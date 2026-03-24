#!/bin/sh
# Serve the built Vue frontend on port 3000
serve -s /app/frontend/dist -l 3000 &

# Run the Flask backend on port 5001 (foreground — container exits if this dies)
cd /app/backend && uv run python run.py
