from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.gui.acquisition import AcquisitionThread, Sample
from src.gui.mpl_canvas import MplPlotCanvas


class MainWindow(QMainWindow):
    def __init__(self, controller, switch, current_source, voltmeter, cfg, parent=None):
        super().__init__(parent)

        self._controller = controller
        self._switch = switch
        self._current_source = current_source
        self._voltmeter = voltmeter
        self._cfg = cfg

        self.setWindowTitle("DAQ / Resistance Acquisition")

        self._thread: Optional[AcquisitionThread] = None
        self._recording = False
        self._csv_fp = None
        self._csv_writer = None

        root = QWidget()
        self.setCentralWidget(root)

        outer = QHBoxLayout(root)

        # Left panel (indicators + old multiplex buttons)
        left = QVBoxLayout()
        outer.addLayout(left, 0)

        self._build_left_panel(left)

        # Center panel (plot + controls)
        center = QVBoxLayout()
        outer.addLayout(center, 1)

        self._build_center_panel(center)

        # Right panel (load/strain indicators)
        right = QVBoxLayout()
        outer.addLayout(right, 0)

        self._build_right_panel(right)

        self.statusBar().showMessage("Ready")

    # -------------------------
    # UI builders
    # -------------------------
    def _build_left_panel(self, left: QVBoxLayout) -> None:
        g = QGroupBox()
        gl = QGridLayout(g)

        r = 0
        gl.addWidget(QLabel("Time (s)"), r, 0)
        self.lbl_time = QLabel("0")
        gl.addWidget(self.lbl_time, r, 1); r += 1

        gl.addWidget(QLabel("Current (A)"), r, 0)
        self.lbl_current = QLabel("0")
        gl.addWidget(self.lbl_current, r, 1); r += 1

        gl.addWidget(QLabel("Voltage (V)"), r, 0)
        self.lbl_voltage = QLabel("0")
        gl.addWidget(self.lbl_voltage, r, 1); r += 1

        gl.addWidget(QLabel("Resistance (Ω)"), r, 0)
        self.lbl_resistance = QLabel("0")
        gl.addWidget(self.lbl_resistance, r, 1); r += 1

        left.addWidget(g)

        # “Old multiplexing code (not necessary)” from the thesis screenshot
        # Provided as placeholders so layout matches; you can remove later.
        self.btn_auto_mux = QPushButton("Automatically Multiplex?")
        self.btn_manual_mux = QPushButton("Manually Multiplex?")
        self.btn_switch_case = QPushButton("Switch Case")

        left.addWidget(self.btn_auto_mux)
        left.addWidget(self.btn_manual_mux)
        left.addWidget(self.btn_switch_case)

        # Small status-ish area (placeholders)
        small = QGroupBox()
        sg = QGridLayout(small)
        sg.addWidget(QLabel("Readings/Case"), 0, 0)
        self.lbl_readings_case = QLabel("0")
        sg.addWidget(self.lbl_readings_case, 0, 1)

        sg.addWidget(QLabel("Switch Case"), 1, 0)
        self.lbl_switch_case = QLabel("0")
        sg.addWidget(self.lbl_switch_case, 1, 1)

        sg.addWidget(QLabel("Compliance"), 2, 0)
        self.lbl_compliance = QLabel("●")  # simple LED-like indicator
        self.lbl_compliance.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        sg.addWidget(self.lbl_compliance, 2, 1)

        left.addWidget(small)
        left.addStretch(1)

    def _build_center_panel(self, center: QVBoxLayout) -> None:
        top = QHBoxLayout()

        top.addWidget(QLabel("Plot Decision"))
        self.cmb_plot = QComboBox()
        self.cmb_plot.addItems(["Resistance vs Time", "Voltage vs Time", "Current vs Time"])
        self.cmb_plot.currentIndexChanged.connect(self._on_plot_changed)
        top.addWidget(self.cmb_plot, 1)

        center.addLayout(top)

        self.plot = MplPlotCanvas()
        center.addWidget(self.plot, 1)

        # Bottom controls row
        bottom = QHBoxLayout()

        self.btn_record = QPushButton("RECORD")
        self.btn_stop = QPushButton("STOP")
        self.btn_reset = QPushButton("Reset")

        self.btn_record.clicked.connect(self._on_record)
        self.btn_stop.clicked.connect(self._on_stop)
        self.btn_reset.clicked.connect(self._on_reset)

        bottom.addWidget(self.btn_record)
        bottom.addWidget(self.btn_stop)
        bottom.addWidget(self.btn_reset)

        bottom.addWidget(QLabel("Current Working Directory"))
        self.txt_workdir = QLineEdit()
        self.txt_workdir.setReadOnly(True)
        self.txt_workdir.setText(self._cfg.paths.default_working_directory or "")
        bottom.addWidget(self.txt_workdir, 1)

        self.btn_browse = QPushButton("…")
        self.btn_browse.clicked.connect(self._on_browse_dir)
        bottom.addWidget(self.btn_browse)

        center.addLayout(bottom)

        # Experiment settings (simple)
        exp = QGroupBox("Experiment Settings")
        el = QGridLayout(exp)

        el.addWidget(QLabel("Force Ch +"), 0, 0)
        self.spin_ch_pos = QSpinBox()
        self.spin_ch_pos.setRange(1, 9999)
        self.spin_ch_pos.setValue(self._cfg.default_experiment.force_channel_pos)
        el.addWidget(self.spin_ch_pos, 0, 1)

        el.addWidget(QLabel("Force Ch -"), 0, 2)
        self.spin_ch_neg = QSpinBox()
        self.spin_ch_neg.setRange(1, 9999)
        self.spin_ch_neg.setValue(self._cfg.default_experiment.force_channel_neg)
        el.addWidget(self.spin_ch_neg, 0, 3)

        el.addWidget(QLabel("Current (A)"), 1, 0)
        self.spin_current = QDoubleSpinBox()
        self.spin_current.setDecimals(12)
        self.spin_current.setRange(-1e3, 1e3)
        self.spin_current.setValue(self._cfg.default_experiment.current_amps)
        el.addWidget(self.spin_current, 1, 1)

        el.addWidget(QLabel("Interval (ms)"), 1, 2)
        self.spin_interval = QSpinBox()
        self.spin_interval.setRange(50, 10000)
        self.spin_interval.setValue(self._cfg.sample_interval_ms)
        el.addWidget(self.spin_interval, 1, 3)

        self.btn_connect = QPushButton("Connect Instruments")
        self.btn_connect.clicked.connect(self._on_connect)
        el.addWidget(self.btn_connect, 2, 0, 1, 2)

        self.btn_disconnect = QPushButton("Disconnect")
        self.btn_disconnect.clicked.connect(self._on_disconnect)
        el.addWidget(self.btn_disconnect, 2, 2, 1, 2)

        center.addWidget(exp)

    def _build_right_panel(self, right: QVBoxLayout) -> None:
        g = QGroupBox("Numeric")
        gl = QGridLayout(g)

        gl.addWidget(QLabel("Load (lbs)"), 0, 0)
        self.lbl_load = QLabel("0")
        gl.addWidget(self.lbl_load, 0, 1)

        gl.addWidget(QLabel("Extension (in)"), 1, 0)
        self.lbl_extension = QLabel("0")
        gl.addWidget(self.lbl_extension, 1, 1)

        gl.addWidget(QLabel("Strain"), 2, 0)
        self.lbl_strain1 = QLabel("0")
        gl.addWidget(self.lbl_strain1, 2, 1)

        gl.addWidget(QLabel("Strain 2"), 3, 0)
        self.lbl_strain2 = QLabel("0")
        gl.addWidget(self.lbl_strain2, 3, 1)

        right.addWidget(g)
        right.addStretch(1)

    # -------------------------
    # Actions
    # -------------------------
    def _on_plot_changed(self) -> None:
        idx = self.cmb_plot.currentIndex()
        if idx == 0:
            self.plot.set_ylabel("Resistance (Ω)")
        elif idx == 1:
            self.plot.set_ylabel("Voltage (V)")
        else:
            self.plot.set_ylabel("Current (A)")
        self.plot.clear()

    def _on_browse_dir(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Select Working Directory")
        if d:
            self.txt_workdir.setText(d)

    def _on_connect(self) -> None:
        if self._cfg.mode != "real":
            self.statusBar().showMessage("Mock mode: connect() skipped")
            return

        try:
            self._switch.connect()
            self._current_source.connect()
            self._voltmeter.connect()
            self.statusBar().showMessage("Connected")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", str(e))

    def _on_disconnect(self) -> None:
        try:
            # Safe even in mock mode if methods exist
            if hasattr(self._voltmeter, "disconnect"):
                self._voltmeter.disconnect()
            if hasattr(self._current_source, "disconnect"):
                self._current_source.disconnect()
            if hasattr(self._switch, "disconnect"):
                self._switch.disconnect()
            self.statusBar().showMessage("Disconnected")
        except Exception as e:
            QMessageBox.critical(self, "Disconnect Error", str(e))

    def _on_record(self) -> None:
        if self._thread and self._thread.isRunning():
            QMessageBox.information(self, "Already Running", "Acquisition is already running.")
            return

        workdir = self.txt_workdir.text().strip()
        if not workdir:
            QMessageBox.warning(self, "Working Directory", "Set a working directory first.")
            return

        out_path = QFileDialog.getSaveFileName(
            self,
            "Select Output CSV",
            str(Path(workdir) / "data.csv"),
            "CSV Files (*.csv)"
        )[0]
        if not out_path:
            return

        try:
            self._start_csv(out_path)
        except Exception as e:
            QMessageBox.critical(self, "File Error", f"Could not open CSV:\n{e}")
            return

        self._recording = True

        self._thread = AcquisitionThread(
            controller=self._controller,
            force_ch_pos=self.spin_ch_pos.value(),
            force_ch_neg=self.spin_ch_neg.value(),
            current_amps=self.spin_current.value(),
            interval_ms=self.spin_interval.value(),
        )
        self._thread.sample_ready.connect(self._on_sample)
        self._thread.status.connect(lambda s: self.statusBar().showMessage(s))
        self._thread.error.connect(self._on_error)

        self._thread.start()

    def _on_stop(self) -> None:
        if self._thread:
            self._thread.stop()
            self._thread.wait(2000)
            self._thread = None

        self._stop_csv()
        self._recording = False
        self.statusBar().showMessage("Stopped")

    def _on_reset(self) -> None:
        self.plot.clear()

    def _on_error(self, msg: str) -> None:
        self._on_stop()
        QMessageBox.critical(self, "Acquisition Error", msg)

    def _on_sample(self, sample: Sample) -> None:
        # Update indicators
        self.lbl_time.setText(f"{sample.t_seconds:.3f}")
        self.lbl_current.setText(f"{sample.current_amps:.6g}")
        self.lbl_voltage.setText(f"{sample.voltage_v:.6g}")
        self.lbl_resistance.setText(f"{sample.resistance_ohms:.6g}")

        self.lbl_load.setText(f"{sample.load_lbs:.6g}")
        self.lbl_extension.setText(f"{sample.extension_in:.6g}")
        self.lbl_strain1.setText(f"{sample.strain_1:.6g}")
        self.lbl_strain2.setText(f"{sample.strain_2:.6g}")

        # Plot based on selector
        idx = self.cmb_plot.currentIndex()
        if idx == 0:
            y = sample.resistance_ohms
        elif idx == 1:
            y = sample.voltage_v
        else:
            y = sample.current_amps

        self.plot.append_point(sample.t_seconds, y)

        # CSV record
        if self._recording:
            self._write_csv(sample)

    # -------------------------
    # CSV
    # -------------------------
    def _start_csv(self, path: str) -> None:
        self._csv_fp = open(path, "w", newline="", encoding="utf-8")
        self._csv_writer = csv.writer(self._csv_fp)
        self._csv_writer.writerow(["t_s", "current_A", "voltage_V", "resistance_ohm", "load_lbs", "extension_in", "strain1", "strain2"])
        self._csv_fp.flush()

    def _write_csv(self, s: Sample) -> None:
        if not self._csv_writer:
            return
        self._csv_writer.writerow([s.t_seconds, s.current_amps, s.voltage_v, s.resistance_ohms, s.load_lbs, s.extension_in, s.strain_1, s.strain_2])
        if self._csv_fp:
            self._csv_fp.flush()

    def _stop_csv(self) -> None:
        try:
            if self._csv_fp:
                self._csv_fp.close()
        finally:
            self._csv_fp = None
            self._csv_writer = None

    def closeEvent(self, event) -> None:
        self._on_stop()
        super().closeEvent(event)
