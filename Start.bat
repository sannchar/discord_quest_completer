@echo off
cd /d "%~dp0"
start "" pythonw main.py
if errorlevel 1 (
    python main.py
)
