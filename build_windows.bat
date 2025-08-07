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
pyinstaller --noconsole --name "MetadataGenerator" --add-data "templates;templates" --add-data "static;static" app.py

echo.
echo ===================================
echo  Build complete!
echo  Find your application in the 'dist' folder.
echo ===================================
pause