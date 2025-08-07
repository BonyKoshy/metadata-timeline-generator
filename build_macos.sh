#!/bin/bash
echo "==================================="
echo " Cleaning up old builds..."
echo "==================================="
rm -rf build/
rm -rf dist/
rm -f MetadataGenerator.spec

echo ""
echo "==================================="
echo " Building macOS Application..."
echo "==================================="
# Using --windowed and adding the --icon flag
pyinstaller --windowed --name "MetadataGenerator" --add-data "templates:templates" --add-data "static:static" --icon="static/images/favicon.png" app.py

echo ""
echo "==================================="
echo " Build complete!"
echo " Find your application in the 'dist' folder."
echo "==================================="