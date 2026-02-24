"""
Multi-gauge plotting canvas for displaying multiple measurement cases simultaneously.
OPTIMIZED VERSION - Uses data decimation for smooth real-time plotting.
"""
from __future__ import annotations

from typing import Dict, List
import numpy as np

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MplMultiGaugeCanvas(FigureCanvas):
    """Canvas that plots multiple gauges with different colors on the same axes."""
    
    # Color scheme for different gauges
    COLORS = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    
    def __init__(self, parent=None):
        fig = Figure()
        super().__init__(fig)
        self.setParent(parent)

        self.ax = fig.add_subplot(111)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Value")
        self.ax.grid(True, alpha=0.3)
        
        # Disable scientific notation offset (use normal notation)
        self.ax.ticklabel_format(style='plain', axis='y', useOffset=False)

        self.fig = fig
        
        # Store data for each gauge/case
        # Key = case name (e.g., "Gauge 1")
        # Value = {'x': deque, 'y': deque, 'line': matplotlib line object}
        self._data: Dict[str, dict] = {}
        
        # Scrolling window settings
        self._window_size = 30.0  # Show last 30 seconds
        
        # Track total points for determining when to update y-limits
        self._total_points = 0
        self._update_ylim_every = 10  # Update y-limits every N points
        
        # Performance: limit max points displayed per series
        self._max_points_displayed = 500  # Only plot last 500 points per gauge
        
        # Batch updates for better performance
        self._pending_updates = []
        self._batch_size = 5  # Update plot every 5 points

    def clear(self) -> None:
        """Clear all data and reset the plot."""
        self._data.clear()
        self.ax.clear()
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Value")
        self.ax.grid(True, alpha=0.3)
        
        # Disable scientific notation offset
        self.ax.ticklabel_format(style='plain', axis='y', useOffset=False)
        
        self._total_points = 0
        self._pending_updates.clear()
        
        self.draw_idle()

    def append_point(self, x: float, y: float, case_name: str) -> None:
        """
        Add a data point for a specific gauge/case.
        
        Args:
            x: Time value
            y: Measurement value (resistance, voltage, etc.)
            case_name: Name of the case/gauge (e.g., "Gauge 1")
        """
        # Create new series if this is the first point for this case
        if case_name not in self._data:
            color_idx = len(self._data) % len(self.COLORS)
            line, = self.ax.plot([], [], 
                                linewidth=1.5, 
                                color=self.COLORS[color_idx],
                                label=case_name,
                                antialiased=True)
            self._data[case_name] = {
                'x': [],
                'y': [],
                'line': line
            }
            # Update legend when new series is added
            self.ax.legend(loc='upper right', framealpha=0.9)
        
        # Append data
        series = self._data[case_name]
        series['x'].append(float(x))
        series['y'].append(float(y))
        
        # PERFORMANCE: Keep only recent data
        # If we have more points than max_points_displayed, remove oldest
        if len(series['x']) > self._max_points_displayed:
            series['x'].pop(0)
            series['y'].pop(0)
        
        self._total_points += 1
        
        # Add to pending updates batch
        self._pending_updates.append((case_name, x, y))
        
        # Only update plot every N points for better performance
        if len(self._pending_updates) >= self._batch_size:
            self._flush_updates()
    
    def _flush_updates(self):
        """Apply all pending updates to the plot."""
        if not self._pending_updates:
            return
        
        # Update all line data at once
        for case_name in set(update[0] for update in self._pending_updates):
            if case_name in self._data:
                series = self._data[case_name]
                series['line'].set_data(series['x'], series['y'])
        
        self._pending_updates.clear()
        
        # Update Y limits periodically to adapt to data
        if self._total_points >= 30 and (self._total_points % self._update_ylim_every == 0 or self._total_points == 30):
            # For multi-gauge, we want to show DETAIL in fluctuations, not just fit all data
            # Strategy: Calculate range based on the VARIANCE of each series
            
            # Collect recent data from each series (last 50 points for responsiveness)
            recent_window = 50
            all_recent_y = []
            series_ranges = []
            
            for series in self._data.values():
                if len(series['y']) > 0:
                    recent = series['y'][-recent_window:] if len(series['y']) > recent_window else series['y']
                    all_recent_y.extend(recent)
                    # Track the range (variation) within this series
                    if len(recent) > 1:
                        series_range = max(recent) - min(recent)
                        series_ranges.append(series_range)
            
            if all_recent_y:
                # Use global min/max of recent data
                y_min = min(all_recent_y)
                y_max = max(all_recent_y)
                
                # Find the largest variation among all series
                max_series_range = max(series_ranges) if series_ranges else 0
                
                # Set padding based on the larger of:
                # 1. 100% of the max series variation (to show detail)
                # 2. 5% of the overall range (minimum padding)
                overall_range = y_max - y_min
                padding = max(max_series_range * 1.0, overall_range * 0.05)
                
                # Apply padding
                if padding > 0:
                    new_y_min = y_min - padding
                    new_y_max = y_max + padding
                else:
                    # Fallback for completely flat data
                    if abs(y_min) > 1e-15:
                        new_y_min = y_min * 0.98
                        new_y_max = y_max * 1.02
                    else:
                        new_y_min = -0.1
                        new_y_max = 0.1
                
                self.ax.set_ylim(new_y_min, new_y_max)
        
        # Set X-axis to show a scrolling window (use the latest time from any series)
        max_time = max((series['x'][-1] for series in self._data.values() if series['x']), default=0)
        if max_time > 0:
            x_min = max(0, max_time - self._window_size)
            self.ax.set_xlim(x_min, max_time)
        
        # Redraw
        self.draw_idle()

    def set_ylabel(self, label: str) -> None:
        """Set the Y-axis label."""
        self.ax.set_ylabel(label)
        self.draw_idle()
    
    def set_window_size(self, seconds: float) -> None:
        """Set the scrolling window size in seconds."""
        self._window_size = float(seconds)
