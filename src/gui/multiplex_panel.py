"""
Multiplexing control panel for switching between multiple measurement cases.
"""
from PySide6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QCheckBox,
    QLabel,
    QPushButton,
    QSpinBox,
)
from PySide6.QtCore import Signal


class MultiplexPanel(QGroupBox):
    """Panel for controlling multiplexed measurements across multiple gauges."""
    
    # Signals
    case_changed = Signal(int)  # Emits index of selected case
    multiplex_toggled = Signal(bool)  # Emits True when multiplexing enabled
    auto_cycle_toggled = Signal(bool)  # Emits True when auto-cycle enabled
    switch_requested = Signal()  # Emits when user clicks "Switch to Next Case" button
    
    def __init__(self, measurement_cases, parent=None):
        super().__init__("Multiplexing", parent)
        
        self._cases = measurement_cases
        self._current_case_idx = 0
        self._readings_count = 0
        
        layout = QVBoxLayout(self)
        
        # Case selector dropdown
        case_row = QHBoxLayout()
        case_row.addWidget(QLabel("Case:"))
        self.cmb_case = QComboBox()
        for case in measurement_cases:
            # Show name and channel pair in dropdown (Bank1/Bank2)
            display_text = f"{case.name} [{case.force_channel_pos}/{case.force_channel_neg}]"
            self.cmb_case.addItem(display_text)
        self.cmb_case.currentIndexChanged.connect(self._on_case_changed)
        case_row.addWidget(self.cmb_case, 1)
        layout.addLayout(case_row)
        
        # Show current channels (Bank 1 / Bank 2)
        channels_label = QLabel()
        channels_label.setWordWrap(True)
        channels_label.setStyleSheet("QLabel { color: #666; font-size: 9pt; }")
        if measurement_cases:
            first_case = measurement_cases[0]
            channels_label.setText(f"Bank 1: {first_case.force_channel_pos} | Bank 2: {first_case.force_channel_neg}")
        self.lbl_channels = channels_label
        layout.addWidget(self.lbl_channels)
        
        # Enable multiplexing checkbox
        self.chk_enable = QCheckBox("Enable Multiplexing")
        self.chk_enable.toggled.connect(self._on_multiplex_toggled)
        layout.addWidget(self.chk_enable)
        
        # Auto cycle checkbox
        self.chk_auto = QCheckBox("Auto Cycle Through Cases")
        self.chk_auto.toggled.connect(self._on_auto_toggled)
        self.chk_auto.setEnabled(False)  # Only enabled when multiplexing is on
        layout.addWidget(self.chk_auto)
        
        # Readings per case (for auto mode)
        readings_row = QHBoxLayout()
        readings_row.addWidget(QLabel("Readings/Case:"))
        self.spin_readings = QSpinBox()
        self.spin_readings.setRange(1, 1000)
        self.spin_readings.setValue(10)
        self.spin_readings.setEnabled(False)
        readings_row.addWidget(self.spin_readings, 1)
        layout.addLayout(readings_row)
        
        # Manual switch button (for manual mode)
        self.btn_next_case = QPushButton("Switch to Next Case")
        self.btn_next_case.clicked.connect(self._on_next_case)
        self.btn_next_case.setEnabled(False)
        layout.addWidget(self.btn_next_case)
        
        # Status indicators
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        current_row = QHBoxLayout()
        current_row.addWidget(QLabel("Current Case:"))
        self.lbl_current_case = QLabel(measurement_cases[0].name if measurement_cases else "None")
        current_row.addWidget(self.lbl_current_case, 1)
        status_layout.addLayout(current_row)
        
        count_row = QHBoxLayout()
        count_row.addWidget(QLabel("Readings:"))
        self.lbl_reading_count = QLabel("0")
        count_row.addWidget(self.lbl_reading_count, 1)
        status_layout.addLayout(count_row)
        
        layout.addWidget(status_group)
        layout.addStretch(1)
    
    def _on_case_changed(self, idx):
        """User manually selected a different case."""
        if idx < 0 or idx >= len(self._cases):
            return
        self._current_case_idx = idx
        self._readings_count = 0
        case = self._cases[idx]
        self.lbl_current_case.setText(case.name)
        self.lbl_channels.setText(f"Bank 1: {case.force_channel_pos} | Bank 2: {case.force_channel_neg}")
        self.lbl_reading_count.setText("0")
        self.case_changed.emit(idx)
    
    def _on_multiplex_toggled(self, checked):
        """Enable/disable multiplexing."""
        self.chk_auto.setEnabled(checked)
        self.btn_next_case.setEnabled(checked and not self.chk_auto.isChecked())
        self.spin_readings.setEnabled(checked and self.chk_auto.isChecked())
        self.cmb_case.setEnabled(not checked)  # Manual case selection only when multiplex is off
        self.multiplex_toggled.emit(checked)
    
    def _on_auto_toggled(self, checked):
        """Enable/disable auto-cycling."""
        self.btn_next_case.setEnabled(not checked and self.chk_enable.isChecked())
        self.spin_readings.setEnabled(checked)
        self.auto_cycle_toggled.emit(checked)
    
    def _on_next_case(self):
        """Manually advance to the next case."""
        if len(self._cases) <= 1:
            return
        # Emit signal to request the switch (main window will handle hardware)
        self.switch_requested.emit()
    
    def increment_reading_count(self):
        """Called by main window each time a sample is taken."""
        self._readings_count += 1
        self.lbl_reading_count.setText(str(self._readings_count))
    
    def reset_reading_count(self):
        """Reset the reading counter (e.g., when switching cases)."""
        self._readings_count = 0
        self.lbl_reading_count.setText("0")
    
    def get_current_case(self):
        """Returns the currently selected MeasurementCase object."""
        if 0 <= self._current_case_idx < len(self._cases):
            return self._cases[self._current_case_idx]
        return None
    
    def is_multiplexing_enabled(self):
        """Returns True if multiplexing is currently enabled."""
        return self.chk_enable.isChecked()
    
    def should_auto_advance(self):
        """Returns True if auto mode is on and enough readings have been taken."""
        if not self.chk_auto.isChecked():
            return False
        return self._readings_count >= self.spin_readings.value()
    
    def auto_advance_case(self):
        """Automatically advance to the next case (used in auto mode)."""
        if len(self._cases) <= 1:
            return
        next_idx = (self._current_case_idx + 1) % len(self._cases)
        self._current_case_idx = next_idx
        case = self._cases[next_idx]
        self.lbl_current_case.setText(case.name)
        self.lbl_channels.setText(f"Bank 1: {case.force_channel_pos} | Bank 2: {case.force_channel_neg}")
        self.reset_reading_count()
