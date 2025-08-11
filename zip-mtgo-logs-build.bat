python -m PyInstaller --console --onefile -i "icon_1.png" zip-mtgo-logs.py

REM Move the built EXE from dist to the project root
if exist "dist\\zip-mtgo-logs.exe" move /y "dist\\zip-mtgo-logs.exe" ".\\zip-mtgo-logs.exe"

REM Clean up build artifacts
rmdir build /s /q
del zip-mtgo-logs.spec
rmdir dist /s /q