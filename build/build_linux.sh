#!/bin/bash
# Build FoodLog for Linux

set -e

echo "Building FoodLog for Linux..."

# Activate virtual environment
source .venv/bin/activate

# Install PyInstaller if needed
pip install pyinstaller

# Create dist directory
mkdir -p dist/FoodLog_Linux

# Run PyInstaller
pyinstaller --onedir \
    --windowed \
    --name foodlog_linux \
    --icon=build/foodlog.ico \
    --distpath=dist/FoodLog_Linux \
    --buildpath=build/temp_linux \
    build/foodlog.spec

# Copy README and any documentation
# cp README.md dist/FoodLog_Linux/
# cp SPEC.md dist/FoodLog_Linux/

echo "Build complete! Binary at: dist/FoodLog_Linux/foodlog_linux/"
echo "To run: dist/FoodLog_Linux/foodlog_linux/foodlog_linux"
