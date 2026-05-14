@echo off
chcp 65001 >nul
echo === Reverse Hex Converter - Builder ===
echo.

echo [1/4] Creating virtual environment in temp directory...
if exist "%TEMP%\revkey_build" rmdir /s /q "%TEMP%\revkey_build"
py -m venv "%TEMP%\revkey_build"
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

echo [2/4] Installing dependencies...
call "%TEMP%\revkey_build\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install pyinstaller tkinterdnd2
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo [3/4] Building EXE...
cd /d "%~dp0"
python -m PyInstaller --onefile --windowed --name "ReverseHexConverter" --icon "icon.ico" --add-data "%TEMP%\revkey_build\Lib\site-packages\tkinterdnd2;tkinterdnd2" reverse_hex_converter.py
if errorlevel 1 (
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo [4/4] Cleaning up build files...
move /Y "dist\ReverseHexConverter.exe" "ReverseHexConverter.exe" >nul 2>&1
rmdir /s /q build >nul 2>&1
rmdir /s /q dist >nul 2>&1
del /q ReverseHexConverter.spec >nul 2>&1

echo.
echo ========================================
echo Build complete: ReverseHexConverter.exe
echo ========================================
pause
