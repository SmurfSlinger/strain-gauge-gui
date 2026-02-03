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
from src.gui.mpl_multi_canvas import MplMultiGaugeCanvas
from src.gui.multiplex_panel import MultiplexPanel
from src.gui.help_dialog import HelpDialog
from src.gui.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    def __init__(self, controller, switch, current_source, voltmeter, cfg, parent=None):
        super().__init__(parent)

        self._controller = controller
        self._switch = switch
        self._current_source = current_source
        self._voltmeter = voltmeter
        self._cfg = cfg

        self.setWindowTitle("DAQ / Resistance Acquisition")

        # Create menu bar
        menubar = self.menuBar()
        
        # Settings menu
        settings_menu = menubar.addMenu("&Settings")
        settings_action = settings_menu.addAction("&Preferences...")
        settings_action.triggered.connect(self._on_open_settings)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_action = help_menu.addAction("&User Guide")
        help_action.triggered.connect(self._on_show_help)

        self._thread: Optional[AcquisitionThread] = None
        self._recording = False
        self._csv_fp = None
        self._csv_writer = None
        
        # Plot update throttling (reduce visual choppiness)
        self._last_plot_update = 0.0
        self._plot_update_interval = 0.5  # Update plot every 0.5 seconds

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

        self.lbl_conn_status = QLabel("Disconnected")
        self.statusBar().addPermanentWidget(self.lbl_conn_status)

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

        # Multiplexing panel
        if self._cfg.measurement_cases:
            self.multiplex_panel = MultiplexPanel(self._cfg.measurement_cases)
            self.multiplex_panel.case_changed.connect(self._on_multiplex_case_changed)
            self.multiplex_panel.switch_requested.connect(self._switch_to_next_case)
            left.addWidget(self.multiplex_panel)
        else:
            self.multiplex_panel = None

        # Compliance indicator
        compliance = QGroupBox("Status")
        cg = QGridLayout(compliance)
        cg.addWidget(QLabel("Compliance"), 0, 0)
        self.lbl_compliance = QLabel("●")
        self.lbl_compliance.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        cg.addWidget(self.lbl_compliance, 0, 1)
        left.addWidget(compliance)

        left.addStretch(1)

    def _build_center_panel(self, center: QVBoxLayout) -> None:
        top = QHBoxLayout()

        top.addWidget(QLabel("Plot Decision"))
        self.cmb_plot = QComboBox()
        self.cmb_plot.addItems(["Resistance vs Time", "Voltage vs Time", "Current vs Time"])
        self.cmb_plot.currentIndexChanged.connect(self._on_plot_changed)
        top.addWidget(self.cmb_plot, 1)

        center.addLayout(top)

        # Create both single and multi-gauge canvases
        # Switch between them based on multiplexing mode
        self.plot_single = MplPlotCanvas()
        self.plot_multi = MplMultiGaugeCanvas()
        
        # Start with single-gauge plot visible
        self.plot = self.plot_single
        center.addWidget(self.plot_single, 1)
        center.addWidget(self.plot_multi, 1)
        self.plot_multi.hide()  # Hide multi-gauge plot initially

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
        ylabel = ""
        if idx == 0:
            ylabel = "Resistance (Ω)"
        elif idx == 1:
            ylabel = "Voltage (V)"
        else:
            ylabel = "Current (A)"
        
        self.plot_single.set_ylabel(ylabel)
        self.plot_multi.set_ylabel(ylabel)
        self.plot_single.clear()
        self.plot_multi.clear()

    def _on_browse_dir(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Select Working Directory")
        if d:
            self.txt_workdir.setText(d)

    def _on_multiplex_case_changed(self, case_idx):
        """User changed which gauge/case to measure."""
        if self.multiplex_panel:
            case = self.multiplex_panel.get_current_case()
            if case:
                self.spin_ch_pos.setValue(case.force_channel_pos)
                self.spin_ch_neg.setValue(case.force_channel_neg)

    def _on_open_settings(self):
        """Open the settings dialog."""
        config_path = Path(__file__).parent / "config.json"
        dialog = SettingsDialog(config_path, parent=self)
        dialog.exec()
    
    def _on_show_help(self):
        """Show the help dialog."""
        dialog = HelpDialog(self)
        dialog.exec()
    
    def _switch_to_next_case(self):
        """Switch to the next measurement case (for multiplexing)."""
        if not self.multiplex_panel or not self._thread or not self._thread.isRunning():
            return
        
        try:
            # Get old channels to open
            old_pos = self.spin_ch_pos.value()
            old_neg = self.spin_ch_neg.value()
            
            # Advance to next case
            self.multiplex_panel.auto_advance_case()
            
            # Get new case
            case = self.multiplex_panel.get_current_case()
            if not case:
                return
            
            new_pos = case.force_channel_pos
            new_neg = case.force_channel_neg
            
            # Update spinboxes
            self.spin_ch_pos.setValue(new_pos)
            self.spin_ch_neg.setValue(new_neg)
            
            # Reconfigure hardware:
            # IMPORTANT: Don't call stop_outputs() - keep current source running!
            # Just switch the relay channels while current is still flowing
            
            # Get old case to properly close all channels
            old_case_idx = (self.multiplex_panel._current_case_idx - 1) % len(self._cfg.measurement_cases)
            old_case = self._cfg.measurement_cases[old_case_idx]
            
            # 1. Open ALL old channels (force + sense if 4-wire)
            for ch in old_case.get_all_channels():
                self._switch.open_channel(ch)
            
            # 2. Close ALL new channels (force + sense if 4-wire)
            for ch in case.get_all_channels():
                self._switch.close_channel(ch)
            
            # Current source stays on - controller remains armed
            # Next take_sample() will measure the new gauge
            
            self.statusBar().showMessage(f"Switched to {case.name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Switch Error", f"Error switching cases: {e}")
            self._on_stop()  # Stop everything if switching fails
                
    def _on_connect(self):
        if self._cfg.mode != "real":
            self._connected = True
            self.lbl_conn_status.setText("Mock mode (connected)")
            return

        try:
            idn_switch = self._switch.connect()
            idn_current = self._current_source.connect()
            idn_meter = self._voltmeter.connect()

            self._connected = True

            msg = f"Connected:\n{idn_switch}\n{idn_current}\n{idn_meter}"

            self.lbl_conn_status.setText("Connected")
            self.statusBar().showMessage("Instruments connected")
            QMessageBox.information(self, "Connection Successful", msg)

        except Exception as e:
            self._connected = False
            self.lbl_conn_status.setText("Connection FAILED")
            QMessageBox.critical(self, "Connection Error", str(e))

    def _on_disconnect(self) -> None:
        try:
            self._connected = False

            if hasattr(self._voltmeter, "disconnect"):
                self._voltmeter.disconnect()
            if hasattr(self._current_source, "disconnect"):
                self._current_source.disconnect()
            if hasattr(self._switch, "disconnect"):
                self._switch.disconnect()

            self.lbl_conn_status.setText("Disconnected")
            self.statusBar().showMessage("Disconnected")
        except Exception as e:
            QMessageBox.critical(self, "Disconnect Error", str(e))

    def _on_record(self) -> None:
        if self._thread is not None:
            QMessageBox.warning(
                self,
                "Busy",
                "Previous acquisition is still stopping. Please wait a moment."
            )
            return

        if self._thread and self._thread.isRunning():
            QMessageBox.information(self, "Already Running", "Acquisition is already running.")
            return

        if self._cfg.mode == "real" and not self._connected:
            QMessageBox.warning(self, "Not Connected", "Click 'Connect Instruments' first.")
            return

        workdir = self.txt_workdir.text().strip()
        if not workdir:
            QMessageBox.warning(self, "Working Directory", "Set a working directory first.")
            return

        # Generate smart filename that doesn't overwrite existing files
        workdir_path = Path(workdir)
        base_name = "data"
        counter = 1
        
        # Find next available filename (data.csv, data_001.csv, data_002.csv, etc.)
        suggested_path = workdir_path / f"{base_name}.csv"
        while suggested_path.exists():
            suggested_path = workdir_path / f"{base_name}_{counter:03d}.csv"
            counter += 1

        out_path = QFileDialog.getSaveFileName(
            self,
            "Select Output CSV",
            str(suggested_path),
            "CSV Files (*.csv)"
        )[0]
        if not out_path:
            return

        ch_pos = int(self.spin_ch_pos.value())
        ch_neg = int(self.spin_ch_neg.value())

        try:
            self._switch.close_channel(ch_pos)
            if ch_neg != ch_pos:
                self._switch.close_channel(ch_neg)
        except Exception as e:
            QMessageBox.critical(self, "Switch Error", str(e))
            return

        # Only after switch is confirmed: open CSV
        try:
            self._start_csv(out_path)
        except Exception as e:
            # If CSV fails, revert switch state
            try:
                self._switch.open_channel(ch_pos)
                if ch_neg != ch_pos:
                    self._switch.open_channel(ch_neg)
            except Exception:
                pass

            QMessageBox.critical(self, "File Error", f"Could not open CSV:\n{e}")
            return

        self._recording = True
        
        # Switch to appropriate plot canvas based on multiplexing
        if self.multiplex_panel and self.multiplex_panel.is_multiplexing_enabled():
            # Use multi-gauge canvas when multiplexing
            self.plot_single.hide()
            self.plot_multi.show()
            self.plot = self.plot_multi
        else:
            # Use single-gauge canvas when not multiplexing
            self.plot_multi.hide()
            self.plot_single.show()
            self.plot = self.plot_single

        # ONLY NOW start the acquisition thread
        self._thread = AcquisitionThread(
            controller=self._controller,
            force_ch_pos=ch_pos,
            force_ch_neg=ch_neg,
            current_amps=self.spin_current.value(),
            interval_ms=self.spin_interval.value(),
        )

        self._thread.sample_ready.connect(self._on_sample)
        self._thread.status.connect(lambda s: self.statusBar().showMessage(s))
        self._thread.error.connect(self._on_error)
        self._thread.finished.connect(self._on_thread_finished)

        self._thread.start()

    def _on_stop(self):
        if self._thread:
            self._thread.stop()
            self._controller.stop_outputs()
            self._thread.wait(2000)
            self._thread = None

        self._stop_csv()
        self._recording = False
        self.statusBar().showMessage("Stopped")

    def _on_reset(self) -> None:
        self.plot_single.clear()
        self.plot_multi.clear()

    def _on_thread_finished(self):
        self._thread = None
        self.statusBar().showMessage("Stopped")

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

        # Plot to the appropriate canvas (throttled for smooth updates)
        # Only update plot if enough time has passed since last update
        if sample.t_seconds - self._last_plot_update >= self._plot_update_interval:
            if self.multiplex_panel and self.multiplex_panel.is_multiplexing_enabled():
                # Multi-gauge mode: include case name for color-coded plotting
                case = self.multiplex_panel.get_current_case()
                case_name = case.name if case else "Unknown"
                self.plot_multi.append_point(sample.t_seconds, y, case_name)
            else:
                # Single-gauge mode: just plot the point
                self.plot_single.append_point(sample.t_seconds, y)
            
            self._last_plot_update = sample.t_seconds

        # CSV record
        if self._recording:
            self._write_csv(sample)
        
        # Handle multiplexing auto-advance
        if self.multiplex_panel and self.multiplex_panel.is_multiplexing_enabled():
            self.multiplex_panel.increment_reading_count()
            
            # Check if we should auto-advance to next case
            if self.multiplex_panel.should_auto_advance():
                self._switch_to_next_case()

    # -------------------------
    # CSV
    # -------------------------
    def _start_csv(self, path: str) -> None:
        from datetime import datetime
        
        self._csv_fp = open(path, "w", newline="", encoding="utf-8")
        self._csv_writer = csv.writer(self._csv_fp)
        
        # Write metadata header (write as plain text, not CSV rows)
        self._csv_fp.write("# Strain Gauge Data Acquisition\n")
        self._csv_fp.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self._csv_fp.write(f"# Current: {self.spin_current.value()} A\n")
        self._csv_fp.write(f"# Channels: +{self.spin_ch_pos.value()}, -{self.spin_ch_neg.value()}\n")
        self._csv_fp.write(f"# Sample Interval: {self.spin_interval.value()} ms\n")
        self._csv_fp.write("\n")  # Blank line
        
        # Column headers with units
        self._csv_writer.writerow([
            "Time (s)",
            "Case",
            "Current (A)", 
            "Voltage (V)",
            "Resistance (Ohm)",
            "Load (lbs)",
            "Extension (in)",
            "Strain 1",
            "Strain 2"
        ])
        self._csv_fp.flush()

    def _write_csv(self, s: Sample) -> None:
        if not self._csv_writer:
            return
        
        # Get current case name if multiplexing
        case_name = ""
        if self.multiplex_panel:
            case = self.multiplex_panel.get_current_case()
            case_name = case.name if case else ""
        
        # Format numbers to be more readable (6 significant figures)
        self._csv_writer.writerow([
            f"{s.t_seconds:.6f}",
            case_name,
            f"{s.current_amps:.6e}",
            f"{s.voltage_v:.6e}",
            f"{s.resistance_ohms:.6e}",
            f"{s.load_lbs:.6f}",
            f"{s.extension_in:.6f}",
            f"{s.strain_1:.6e}",
            f"{s.strain_2:.6e}"
        ])
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
