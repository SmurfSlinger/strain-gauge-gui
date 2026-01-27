from __future__ import annotations

import os
os.environ["PYVISA_LIBRARY"] = r"C:\Windows\System32\visa64.dll"

import sys
from PySide6.QtWidgets import QApplication



import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from src.gui.config_loader import load_config
from src.gui.hardware_factory import build_controller
from src.gui.main_window import MainWindow


def main() -> int:
    cfg = load_config(Path(__file__).parent / "config.json")
    controller, switch, current_source, voltmeter = build_controller(cfg)

    app = QApplication(sys.argv)
    w = MainWindow(controller, switch, current_source, voltmeter, cfg)
    w.resize(1200, 650)
    w.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
