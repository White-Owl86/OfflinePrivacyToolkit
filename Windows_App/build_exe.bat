@echo off
title Build Standalone Windows Executable
echo ========================================================
echo   Packaging Offline Privacy Toolkit to Standalone EXE
echo ========================================================
echo.
cd /d "%~dp0"

echo [1/3] Checking PyInstaller...
python -m pip install pyinstaller --quiet

echo [2/3] Compiling into portable single executable...
pyinstaller --noconfirm --onedir --windowed ^
    --name "OfflinePrivacyToolkit" ^
    --icon "assets\app_icon.ico" ^
    --add-data "assets;assets" ^
    --add-data "tessdata;tessdata" ^
    --add-data "src;src" ^
    --hidden-import "customtkinter" ^
    --hidden-import "PIL" ^
    --hidden-import "pypdf" ^
    --hidden-import "fitz" ^
    --hidden-import "pytesseract" ^
    --hidden-import "arabic_reshaper" ^
    --hidden-import "bidi.algorithm" ^
    src\main.py

echo.
echo [3/3] Build finished!
echo Executable is located at: %~dp0dist\OfflinePrivacyToolkit\OfflinePrivacyToolkit.exe
pause
