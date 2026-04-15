#!/bin/bash
# SnapStash First Boot Script
# Runs once on first boot to build and start Docker containers

set -e

echo "🚀 SnapStash first boot — building containers..."

cd /opt/snapstash

# Build and start docker compose
docker compose build
docker compose up -d

# Mark as initialized
touch /opt/snapstash/.initialized

echo "✅ SnapStash is ready!"
echo "   Open http://snapstash.local in your browser"
