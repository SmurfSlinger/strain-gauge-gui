"""
Strain Gauge DAQ Launcher
Double-click this file to start the application (no console window)
"""
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set VISA library path
os.environ["PYVISA_LIBRARY"] = r"C:\Windows\System32\visa64.dll"

# Suppress Qt logging warnings
import logging
logging.getLogger().setLevel(logging.CRITICAL)

# Launch the application
from src.gui.app import main
sys.exit(main())
