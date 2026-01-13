#!/bin/bash

# Helper script to run evaluations easily

if [ $# -lt 2 ]; then
    echo "Usage: ./run_evaluation.sh <video_name> <session_id>"
    echo ""
    echo "Example:"
    echo "  ./run_evaluation.sh trim.mp4 20260113_053847"
    echo ""
    echo "Available sessions:"
    docker exec basketball-tracker-backend ls -1 /tmp/detections/ | grep metadata.json | sed 's/_metadata.json//'
    exit 1
fi

VIDEO_NAME=$1
SESSION_ID=$2

# Copy session metadata from container to local /tmp
echo "📦 Copying session data from container..."
docker cp basketball-tracker-backend:/tmp/detections/${SESSION_ID}_metadata.json /tmp/

if [ $? -ne 0 ]; then
    echo "❌ Failed to copy session metadata. Check if session_id is correct."
    exit 1
fi

# Run evaluation
echo "🚀 Running evaluation..."
cd "$(dirname "$0")"
python3 evaluate.py "$VIDEO_NAME" "$SESSION_ID"
