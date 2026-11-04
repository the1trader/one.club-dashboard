#!/bin/bash
set -e

echo "🚀 Starting one.club Institutional Trading Terminal..."

# Sync database
python3 scripts/sync_db.py

# Start background server
python3 server.py
