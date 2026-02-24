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
    QScrollArea,
    QWidget,
)
from PySide6.QtCore import Signal


class MultiplexPanel(QGroupBox):
    """Panel for controlling multiplexed measurements across multiple gauges."""
    
    # Signals
    case_changed = Signal(int)  # Emits index of selected case
    multiplex_toggled = Signal(bool)  # Emits True when multiplexing enabled
    auto_cycle_toggled = Signal(bool)  # Emits True when auto-cycle enabled
    switch_requested = Signal()  # Emits when user requests a case switch
    
    def __init__(self, measurement_cases, parent=None):
        super().__init__("Multiplexing", parent)
        
        self._cases = measurement_cases
        self._current_case_idx = 0
        self._readings_count = 0
        
        layout = QVBoxLayout(self)
        
        # Status indicators at top
        status_group = QGroupBox("Current Status")
        status_layout = QVBoxLayout(status_group)
        
        current_row = QHBoxLayout()
        current_row.addWidget(QLabel("Active Case:"))
        self.lbl_current_case = QLabel(measurement_cases[0].name if measurement_cases else "None")
        self.lbl_current_case.setStyleSheet("QLabel { font-weight: bold; color: #2c5aa0; }")
        current_row.addWidget(self.lbl_current_case, 1)
        status_layout.addLayout(current_row)
        
        # Show current channels (Bank 1 / Bank 2)
        channels_label = QLabel()
        channels_label.setWordWrap(True)
        channels_label.setStyleSheet("QLabel { color: #666; font-size: 9pt; }")
        if measurement_cases:
            first_case = measurement_cases[0]
            channels_label.setText(f"Bank 1: {first_case.force_channel_pos} | Bank 2: {first_case.force_channel_neg}")
        self.lbl_channels = channels_label
        status_layout.addWidget(self.lbl_channels)
        
        count_row = QHBoxLayout()
        count_row.addWidget(QLabel("Readings:"))
        self.lbl_reading_count = QLabel("0")
        count_row.addWidget(self.lbl_reading_count, 1)
        status_layout.addLayout(count_row)
        
        layout.addWidget(status_group)
        
        # Available cases list with checkboxes and SWITCH TO buttons
        cases_group = QGroupBox("Available Cases")
        cases_layout = QVBoxLayout(cases_group)
        
        # Scrollable area for case list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(250)
        scroll.setMaximumHeight(300)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        scroll_layout.setSpacing(5)
        
        # Create checkbox + button for each case
        self._case_checkboxes = []
        self._case_buttons = []
        
        for i, case in enumerate(measurement_cases):
            row = QHBoxLayout()
            row.setSpacing(5)
            
            # Checkbox (enabled by default)
            chk = QCheckBox()
            chk.setChecked(True)  # All enabled by default
            chk.setToolTip("Enable/disable this case in auto-cycle")
            self._case_checkboxes.append(chk)
            row.addWidget(chk)
            
            # Case info label
            mode_label = "4W" if case.is_4_wire() else "2W"
            info_text = f"{case.name} ({case.force_channel_pos}/{case.force_channel_neg})"
            lbl = QLabel(info_text)
            lbl.setStyleSheet("QLabel { font-size: 8pt; }")
            row.addWidget(lbl, 1)
            
            # SWITCH TO button
            btn = QPushButton("SWITCH TO")
            btn.setMaximumWidth(90)
            btn.setStyleSheet("QPushButton { font-size: 8pt; padding: 3px; }")
            # Use a proper closure to capture the index
            btn.clicked.connect(self._make_switch_handler(i))
            btn.setToolTip(f"Switch to {case.name} immediately")
            self._case_buttons.append(btn)
            row.addWidget(btn)
            
            scroll_layout.addLayout(row)
        
        scroll_layout.addStretch(1)
        scroll.setWidget(scroll_widget)
        cases_layout.addWidget(scroll)
        layout.addWidget(cases_group)
        
        # Update button states for initial case
        self._update_case_button_states()
        
        # Enable multiplexing checkbox
        self.chk_enable = QCheckBox("Enable Multiplexing")
        self.chk_enable.toggled.connect(self._on_multiplex_toggled)
        layout.addWidget(self.chk_enable)
        
        # Auto cycle checkbox
        self.chk_auto = QCheckBox("Auto Cycle (Enabled Cases Only)")
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
        
        layout.addStretch(1)
    
    def _make_switch_handler(self, case_idx):
        """Create a handler that properly captures the case index."""
        return lambda: self._on_switch_to_case(case_idx)
    
    def _on_switch_to_case(self, idx):
        """User clicked SWITCH TO button for a specific case."""
        if idx < 0 or idx >= len(self._cases):
            return
        if idx == self._current_case_idx:
            return  # Already on this case
        
        # Update current case
        self._current_case_idx = idx
        self._readings_count = 0
        case = self._cases[idx]
        self.lbl_current_case.setText(case.name)
        self.lbl_channels.setText(f"Bank 1: {case.force_channel_pos} | Bank 2: {case.force_channel_neg}")
        self.lbl_reading_count.setText("0")
        
        # Update button states (disable current case button)
        self._update_case_button_states()
        
        # Emit signals to trigger hardware switch
        self.case_changed.emit(idx)
        self.switch_requested.emit()
    
    def _update_case_button_states(self):
        """Update SWITCH TO button states based on current case."""
        for i, btn in enumerate(self._case_buttons):
            # Disable button for currently active case
            btn.setEnabled(i != self._current_case_idx)
            if i == self._current_case_idx:
                btn.setStyleSheet("QPushButton { font-size: 8pt; padding: 3px; background-color: #d0d0d0; }")
            else:
                btn.setStyleSheet("QPushButton { font-size: 8pt; padding: 3px; }")
    
    def _on_multiplex_toggled(self, checked):
        """Enable/disable multiplexing."""
        self.chk_auto.setEnabled(checked)
        self.spin_readings.setEnabled(checked and self.chk_auto.isChecked())
        self.multiplex_toggled.emit(checked)
    
    def _on_auto_toggled(self, checked):
        """Enable/disable auto-cycling."""
        self.spin_readings.setEnabled(checked)
        self.auto_cycle_toggled.emit(checked)
    
    def _get_enabled_case_indices(self):
        """Returns list of indices for enabled (checked) cases."""
        return [i for i, chk in enumerate(self._case_checkboxes) if chk.isChecked()]
    
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
        """Automatically advance to the next enabled case (used in auto mode)."""
        enabled_indices = self._get_enabled_case_indices()
        
        if len(enabled_indices) <= 1:
            return  # No point advancing if 0 or 1 cases enabled
        
        # Find next enabled case after current
        current_pos = enabled_indices.index(self._current_case_idx) if self._current_case_idx in enabled_indices else -1
        next_pos = (current_pos + 1) % len(enabled_indices)
        next_idx = enabled_indices[next_pos]
        
        self._current_case_idx = next_idx
        case = self._cases[next_idx]
        self.lbl_current_case.setText(case.name)
        self.lbl_channels.setText(f"Bank 1: {case.force_channel_pos} | Bank 2: {case.force_channel_neg}")
        self.reset_reading_count()
        
        # Update button states
        self._update_case_button_states()
