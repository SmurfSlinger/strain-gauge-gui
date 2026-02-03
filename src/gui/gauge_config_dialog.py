"""
Gauge configuration dialog for setting up measurement cases.
"""
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QComboBox,
    QLineEdit,
    QSpinBox,
    QMessageBox,
)
from PySide6.QtCore import Qt

from src.gui.config_loader import MeasurementCase


class GaugeConfigDialog(QDialog):
    """Dialog for adding/editing/deleting measurement gauges."""
    
    def __init__(self, measurement_cases, allowed_channels, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Measurement Gauges")
        self.resize(900, 500)
        
        self._cases = list(measurement_cases)  # Make a copy
        self._allowed_channels = allowed_channels
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLineEdit()
        instructions.setReadOnly(True)
        instructions.setText("Add, edit, or remove measurement gauges. Each gauge can be 2-wire or 4-wire.")
        instructions.setStyleSheet("QLineEdit { background: #f0f0f0; border: none; }")
        layout.addWidget(instructions)
        
        # Table for displaying gauges
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Name", "Wire Mode", "Force+", "Force-", "Sense+", "Sense-", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        # Populate table
        self._populate_table()
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("Add New Gauge")
        self.btn_add.clicked.connect(self._add_gauge)
        btn_layout.addWidget(self.btn_add)
        
        btn_layout.addStretch()
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        self.btn_save = QPushButton("Save Configuration")
        self.btn_save.clicked.connect(self._save_config)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)
    
    def _populate_table(self):
        """Populate the table with current gauge configurations."""
        self.table.setRowCount(len(self._cases))
        
        for row, case in enumerate(self._cases):
            # Name
            name_edit = QLineEdit(case.name)
            self.table.setCellWidget(row, 0, name_edit)
            
            # Wire mode dropdown
            mode_combo = QComboBox()
            mode_combo.addItems(["2-wire", "4-wire"])
            mode_combo.setCurrentText(case.wire_mode)
            mode_combo.currentTextChanged.connect(lambda text, r=row: self._on_wire_mode_changed(r, text))
            self.table.setCellWidget(row, 1, mode_combo)
            
            # Force+ channel
            force_pos_spin = QSpinBox()
            force_pos_spin.setRange(1001, 1040)
            force_pos_spin.setValue(case.force_channel_pos)
            self.table.setCellWidget(row, 2, force_pos_spin)
            
            # Force- channel
            force_neg_spin = QSpinBox()
            force_neg_spin.setRange(1001, 1040)
            force_neg_spin.setValue(case.force_channel_neg)
            self.table.setCellWidget(row, 3, force_neg_spin)
            
            # Sense+ channel (only for 4-wire)
            sense_pos_spin = QSpinBox()
            sense_pos_spin.setRange(1001, 1040)
            sense_pos_spin.setValue(case.sense_channel_pos if case.sense_channel_pos else 1001)
            sense_pos_spin.setEnabled(case.is_4_wire())
            self.table.setCellWidget(row, 4, sense_pos_spin)
            
            # Sense- channel (only for 4-wire)
            sense_neg_spin = QSpinBox()
            sense_neg_spin.setRange(1001, 1040)
            sense_neg_spin.setValue(case.sense_channel_neg if case.sense_channel_neg else 1002)
            sense_neg_spin.setEnabled(case.is_4_wire())
            self.table.setCellWidget(row, 5, sense_neg_spin)
            
            # Delete button
            btn_delete = QPushButton("Delete")
            btn_delete.clicked.connect(lambda checked, r=row: self._delete_gauge(r))
            self.table.setCellWidget(row, 6, btn_delete)
    
    def _on_wire_mode_changed(self, row, mode):
        """Enable/disable sense channels based on wire mode."""
        is_4_wire = (mode == "4-wire")
        sense_pos_spin = self.table.cellWidget(row, 4)
        sense_neg_spin = self.table.cellWidget(row, 5)
        if sense_pos_spin:
            sense_pos_spin.setEnabled(is_4_wire)
        if sense_neg_spin:
            sense_neg_spin.setEnabled(is_4_wire)
    
    def _add_gauge(self):
        """Add a new gauge row."""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Name
        name_edit = QLineEdit(f"Gauge {row + 1}")
        self.table.setCellWidget(row, 0, name_edit)
        
        # Wire mode
        mode_combo = QComboBox()
        mode_combo.addItems(["2-wire", "4-wire"])
        mode_combo.currentTextChanged.connect(lambda text, r=row: self._on_wire_mode_changed(r, text))
        self.table.setCellWidget(row, 1, mode_combo)
        
        # Force+ channel
        force_pos_spin = QSpinBox()
        force_pos_spin.setRange(1001, 1040)
        force_pos_spin.setValue(1001 + row * 2)
        self.table.setCellWidget(row, 2, force_pos_spin)
        
        # Force- channel
        force_neg_spin = QSpinBox()
        force_neg_spin.setRange(1001, 1040)
        force_neg_spin.setValue(1002 + row * 2)
        self.table.setCellWidget(row, 3, force_neg_spin)
        
        # Sense+ channel
        sense_pos_spin = QSpinBox()
        sense_pos_spin.setRange(1001, 1040)
        sense_pos_spin.setValue(1001)
        sense_pos_spin.setEnabled(False)  # 2-wire by default
        self.table.setCellWidget(row, 4, sense_pos_spin)
        
        # Sense- channel
        sense_neg_spin = QSpinBox()
        sense_neg_spin.setRange(1001, 1040)
        sense_neg_spin.setValue(1002)
        sense_neg_spin.setEnabled(False)  # 2-wire by default
        self.table.setCellWidget(row, 5, sense_neg_spin)
        
        # Delete button
        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(lambda checked, r=row: self._delete_gauge(r))
        self.table.setCellWidget(row, 6, btn_delete)
    
    def _delete_gauge(self, row):
        """Delete a gauge row."""
        reply = QMessageBox.question(
            self,
            "Delete Gauge",
            f"Are you sure you want to delete this gauge?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.table.removeRow(row)
    
    def _save_config(self):
        """Validate and save the configuration."""
        new_cases = []
        
        for row in range(self.table.rowCount()):
            # Get values from widgets
            name = self.table.cellWidget(row, 0).text().strip()
            wire_mode = self.table.cellWidget(row, 1).currentText()
            force_pos = self.table.cellWidget(row, 2).value()
            force_neg = self.table.cellWidget(row, 3).value()
            sense_pos = self.table.cellWidget(row, 4).value()
            sense_neg = self.table.cellWidget(row, 5).value()
            
            # Validate
            if not name:
                QMessageBox.warning(self, "Invalid Name", f"Row {row + 1}: Gauge name cannot be empty.")
                return
            
            # Check for duplicate channels
            if force_pos == force_neg:
                QMessageBox.warning(self, "Invalid Channels", 
                    f"Row {row + 1}: Force+ and Force- cannot be the same channel.")
                return
            
            if wire_mode == "4-wire":
                if sense_pos == sense_neg:
                    QMessageBox.warning(self, "Invalid Channels",
                        f"Row {row + 1}: Sense+ and Sense- cannot be the same channel.")
                    return
                
                # Check for overlaps between force and sense
                channels_used = {force_pos, force_neg, sense_pos, sense_neg}
                if len(channels_used) != 4:
                    QMessageBox.warning(self, "Invalid Channels",
                        f"Row {row + 1}: All 4 channels must be unique for 4-wire measurements.")
                    return
            
            # Create measurement case
            case = MeasurementCase(
                name=name,
                force_channel_pos=force_pos,
                force_channel_neg=force_neg,
                wire_mode=wire_mode,
                sense_channel_pos=sense_pos if wire_mode == "4-wire" else None,
                sense_channel_neg=sense_neg if wire_mode == "4-wire" else None
            )
            new_cases.append(case)
        
        if not new_cases:
            QMessageBox.warning(self, "No Gauges", "You must have at least one gauge configured.")
            return
        
        self._cases = new_cases
        self.accept()
    
    def get_measurement_cases(self):
        """Return the configured measurement cases."""
        return self._cases
