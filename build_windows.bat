@echo OFF
echo.
echo ===================================
echo  Cleaning up old builds...
echo ===================================
rmdir /s /q build
rmdir /s /q dist
del MetadataGenerator.spec

echo.
echo ===================================
echo  Building Windows Application...
echo ===================================
pyinstaller --windowed --name "MetadataGenerator" --add-data "templates;templates" --add-data "static;static" --icon="static/images/favicon.ico" app.py

echo.
echo ===================================
echo  Build complete!
echo  Your new application is in the 'dist' folder.
echo ===================================
pause