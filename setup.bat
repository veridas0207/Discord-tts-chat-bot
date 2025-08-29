@echo off

REM Change directory to the script's location
cd /d "%~dp0"

setlocal

echo ##################################################################
echo ##                                                              ##
echo ##      Discord Bot Dependency Installer for Windows          ##
echo ##                                                              ##
echo ##################################################################
echo.

REM Check if python is installed
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8+ and add it to your PATH environment variable.
    pause
    exit /b 1
)

echo Found Python installation:
python --version
echo.

echo Installing required packages from requirements.txt globally...
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ##################################################################
    echo ##                                                              ##
    echo ##  Error: Failed to install packages. Please check the output  ##
    echo ##  above for details. You might need to run this script      ##
    echo ##  as an administrator.                                      ##
    echo ##                                                              ##
    echo ##################################################################
    pause
    exit /b 1
)

echo.
echo ##################################################################
echo ##                                                              ##
echo ##            Setup complete! Packages are installed.           ##
    echo ##                                                              ##
echo ##################################################################
echo.
echo You can now run the bot using:
echo    python bot.py
echo.
pause
