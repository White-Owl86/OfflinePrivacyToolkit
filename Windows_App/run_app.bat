@echo off
title Offline Privacy & Document Toolkit
echo ========================================================
echo   Offline Privacy & Document Toolkit (Air-Gapped Edition)
echo   100%% Local & Offline Document Processor
echo ========================================================
echo.
cd /d "%~dp0"

echo [1/2] Verifying dependencies...
python -m pip install -r requirements.txt --quiet

echo [2/2] Launching Application...
python src\main.py

pause
