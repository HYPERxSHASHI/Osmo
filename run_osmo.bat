@echo off
title OSMO Personal AI Assistant
cd /d "%~dp0"

echo [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
  echo Python is not installed or not available in PATH.
  pause
  exit /b 1
)

echo [2/3] Installing required modules...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Failed to install dependencies.
  pause
  exit /b 1
)

echo [3/3] Starting OSMO...
python osmo.py
pause
