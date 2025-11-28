#!/bin/bash
cd "$(dirname "$0")/.."
uv run ./backend/app/scripts/import_data.py

