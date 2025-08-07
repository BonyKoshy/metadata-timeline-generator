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
# Note the ':' separator for --add-data on macOS/Linux
pyinstaller --noconsole --name "MetadataGenerator" --add-data "templates:templates" --add-data "static:static" app.py

echo ""
echo "==================================="
echo " Build complete!"
echo " Find your application in the 'dist' folder."
echo "==================================="