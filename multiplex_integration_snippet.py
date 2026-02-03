# Add this method to MainWindow class after _build_left_panel

def _on_multiplex_case_changed(self, case_idx):
    """User changed which gauge/case to measure."""
    if self.multiplex_panel:
        case = self.multiplex_panel.get_current_case()
        if case:
            # Update the channel spinboxes to match the selected case
            self.spin_ch_pos.setValue(case.force_channel_pos)
            self.spin_ch_neg.setValue(case.force_channel_neg)
