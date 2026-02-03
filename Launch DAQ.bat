@echo off
REM Strain Gauge DAQ Launcher
REM Double-click this file to start the application

cd /d "%~dp0"

REM Try to find and activate virtual environment
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" -m src.gui
) else if exist "venv\Scripts\pythonw.exe" (
    start "" "venv\Scripts\pythonw.exe" -m src.gui
) else (
    REM Fall back to system Python
    start "" pythonw -m src.gui
)
