#!/bin/bash
# Symphony v2.1.2 Linux/Mac Install

echo ""
echo "========================================"
echo "  Symphony v2.1.2 Installing..."
echo "========================================"
echo ""

echo "[1/2] Creating directory..."
mkdir -p ~/.openclaw/workspace/skills/symphony

echo "[2/2] Copying files..."
cp -r * ~/.openclaw/workspace/skills/symphony/

echo ""
echo "========================================"
echo "  Done!"
echo "========================================"
echo ""
echo "Next step: Edit config.py with your API key"
echo ""
