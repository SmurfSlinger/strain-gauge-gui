"""
Settings dialog for configuring measurement cases (gauges) and other options.
"""
from pathlib import Path
import json
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QGroupBox,
    QFormLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QSpinBox,
    QHeaderView,
    QMessageBox,
    QLabel,
)
from PySide6.QtCore import Qt


class SettingsDialog(QDialog):
    """Dialog for editing configuration including measurement cases."""
    
    def __init__(self, config_path: Path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(700, 500)
        
        self.config_path = config_path
        self.config_data = self._load_config()
        
        layout = QVBoxLayout(self)
        
        # Create tabbed interface
        tabs = QTabWidget()
        tabs.addTab(self._create_gauges_tab(), "Measurement Gauges")
        tabs.addTab(self._create_general_tab(), "General Settings")
        
        layout.addWidget(tabs)
        
        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_save = QPushButton("Save && Restart Required")
        btn_save.clicked.connect(self._on_save)
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
    
    def _load_config(self):
        """Load the current config file."""
        return json.loads(self.config_path.read_text())
    
    def _create_gauges_tab(self):
        """Create the gauges configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Info label
        info = QLabel("Configure measurement gauges/cases. Each gauge can use 2-wire or 4-wire mode.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Table for gauges
        self.gauge_table = QTableWidget()
        self.gauge_table.setColumnCount(7)
        self.gauge_table.setHorizontalHeaderLabels([
            "Name", "Wire Mode", "Force Ch +", "Force Ch -", 
            "Sense Ch +", "Sense Ch -", "Actions"
        ])
        self.gauge_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Populate table with existing gauges
        self._populate_gauge_table()
        
        layout.addWidget(self.gauge_table)
        
        # Add gauge button
        btn_add = QPushButton("Add New Gauge")
        btn_add.clicked.connect(self._on_add_gauge)
        layout.addWidget(btn_add)
        
        return widget
    
    def _create_general_tab(self):
        """Create the general settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Sample interval
        group = QGroupBox("Acquisition Settings")
        form = QFormLayout(group)
        
        self.spin_interval = QSpinBox()
        self.spin_interval.setRange(50, 10000)
        self.spin_interval.setValue(self.config_data.get("sample_interval_ms", 100))
        self.spin_interval.setSuffix(" ms")
        form.addRow("Sample Interval:", self.spin_interval)
        
        layout.addWidget(group)
        layout.addStretch()
        
        return widget
    
    def _populate_gauge_table(self):
        """Populate the gauge table with existing measurement cases."""
        cases = self.config_data.get("measurement_cases", [])
        self.gauge_table.setRowCount(len(cases))
        
        for row, case in enumerate(cases):
            # Name
            name_item = QTableWidgetItem(case["name"])
            self.gauge_table.setItem(row, 0, name_item)
            
            # Wire mode dropdown
            wire_combo = QComboBox()
            wire_combo.addItems(["2-wire", "4-wire"])
            wire_combo.setCurrentText(case.get("wire_mode", "2-wire"))
            wire_combo.currentTextChanged.connect(lambda text, r=row: self._on_wire_mode_changed(r, text))
            self.gauge_table.setCellWidget(row, 1, wire_combo)
            
            # Force channels
            force_pos = QSpinBox()
            force_pos.setRange(1001, 1040)
            force_pos.setValue(case["force_channel_pos"])
            self.gauge_table.setCellWidget(row, 2, force_pos)
            
            force_neg = QSpinBox()
            force_neg.setRange(1001, 1040)
            force_neg.setValue(case["force_channel_neg"])
            self.gauge_table.setCellWidget(row, 3, force_neg)
            
            # Sense channels
            sense_pos = QSpinBox()
            sense_pos.setRange(1001, 1040)
            sense_pos.setValue(case.get("sense_channel_pos") or 1001)
            sense_pos.setEnabled(case.get("wire_mode") == "4-wire")
            self.gauge_table.setCellWidget(row, 4, sense_pos)
            
            sense_neg = QSpinBox()
            sense_neg.setRange(1001, 1040)
            sense_neg.setValue(case.get("sense_channel_neg") or 1002)
            sense_neg.setEnabled(case.get("wire_mode") == "4-wire")
            self.gauge_table.setCellWidget(row, 5, sense_neg)
            
            # Delete button
            btn_delete = QPushButton("Delete")
            btn_delete.clicked.connect(lambda checked, r=row: self._on_delete_gauge(r))
            self.gauge_table.setCellWidget(row, 6, btn_delete)
    
    def _on_wire_mode_changed(self, row, mode):
        """Enable/disable sense channel spinboxes based on wire mode."""
        is_4wire = (mode == "4-wire")
        sense_pos = self.gauge_table.cellWidget(row, 4)
        sense_neg = self.gauge_table.cellWidget(row, 5)
        if sense_pos:
            sense_pos.setEnabled(is_4wire)
        if sense_neg:
            sense_neg.setEnabled(is_4wire)
    
    def _on_add_gauge(self):
        """Add a new gauge row to the table."""
        row = self.gauge_table.rowCount()
        self.gauge_table.insertRow(row)
        
        # Name
        name_item = QTableWidgetItem(f"Gauge {row + 1}")
        self.gauge_table.setItem(row, 0, name_item)
        
        # Wire mode
        wire_combo = QComboBox()
        wire_combo.addItems(["2-wire", "4-wire"])
        wire_combo.currentTextChanged.connect(lambda text, r=row: self._on_wire_mode_changed(r, text))
        self.gauge_table.setCellWidget(row, 1, wire_combo)
        
        # Channels - suggest next available channels
        next_ch = 1001 + (row * 2)
        
        force_pos = QSpinBox()
        force_pos.setRange(1001, 1040)
        force_pos.setValue(next_ch)
        self.gauge_table.setCellWidget(row, 2, force_pos)
        
        force_neg = QSpinBox()
        force_neg.setRange(1001, 1040)
        force_neg.setValue(next_ch + 1)
        self.gauge_table.setCellWidget(row, 3, force_neg)
        
        sense_pos = QSpinBox()
        sense_pos.setRange(1001, 1040)
        sense_pos.setValue(next_ch + 2)
        sense_pos.setEnabled(False)
        self.gauge_table.setCellWidget(row, 4, sense_pos)
        
        sense_neg = QSpinBox()
        sense_neg.setRange(1001, 1040)
        sense_neg.setValue(next_ch + 3)
        sense_neg.setEnabled(False)
        self.gauge_table.setCellWidget(row, 5, sense_neg)
        
        # Delete button
        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(lambda checked, r=row: self._on_delete_gauge(r))
        self.gauge_table.setCellWidget(row, 6, btn_delete)
    
    def _on_delete_gauge(self, row):
        """Delete a gauge row from the table."""
        reply = QMessageBox.question(
            self,
            "Delete Gauge",
            f"Delete gauge '{self.gauge_table.item(row, 0).text()}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.gauge_table.removeRow(row)
    
    def _on_save(self):
        """Save the configuration to file."""
        # Update measurement cases from table
        cases = []
        for row in range(self.gauge_table.rowCount()):
            name_item = self.gauge_table.item(row, 0)
            wire_combo = self.gauge_table.cellWidget(row, 1)
            force_pos = self.gauge_table.cellWidget(row, 2)
            force_neg = self.gauge_table.cellWidget(row, 3)
            sense_pos = self.gauge_table.cellWidget(row, 4)
            sense_neg = self.gauge_table.cellWidget(row, 5)
            
            wire_mode = wire_combo.currentText()
            
            case = {
                "name": name_item.text(),
                "wire_mode": wire_mode,
                "force_channel_pos": force_pos.value(),
                "force_channel_neg": force_neg.value(),
                "sense_channel_pos": sense_pos.value() if wire_mode == "4-wire" else None,
                "sense_channel_neg": sense_neg.value() if wire_mode == "4-wire" else None
            }
            cases.append(case)
        
        self.config_data["measurement_cases"] = cases
        self.config_data["sample_interval_ms"] = self.spin_interval.value()
        
        # Save to file
        try:
            self.config_path.write_text(json.dumps(self.config_data, indent=2))
            QMessageBox.information(
                self,
                "Settings Saved",
                "Settings saved successfully!\n\nPlease restart the application for changes to take effect."
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save settings:\n{e}"
            )
