from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MplPlotCanvas(FigureCanvas):
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
        
        self._x: List[float] = []
        self._y: List[float] = []
        (self._line,) = self.ax.plot([], [], linewidth=1.5)

        self.fig = fig
        
        # Scrolling window settings
        self._window_size = 30.0  # Show last 30 seconds
        self._update_ylim_every = 10  # Update y-limits every N points
        self._point_count = 0

    def clear(self) -> None:
        self._x.clear()
        self._y.clear()
        self._line.set_data([], [])
        self._point_count = 0
        self.ax.relim()
        self.ax.autoscale_view()
        self.draw_idle()

    def append_point(self, x: float, y: float) -> None:
        self._x.append(float(x))
        self._y.append(float(y))
        self._line.set_data(self._x, self._y)
        self._point_count += 1
        
        # Update Y limits periodically to adapt to data
        if len(self._y) >= 10 and (self._point_count % self._update_ylim_every == 0 or len(self._y) == 10):
            # Use ALL data for y-limits to see full experiment range
            y_min = min(self._y)
            y_max = max(self._y)
            y_range = y_max - y_min
            
            # Add 50% padding on top and bottom for wider view
            if y_range > 0:
                padding = y_range * 0.5
                new_y_min = y_min - padding
                new_y_max = y_max + padding
            else:
                # If all values are the same, use ±2% of the value
                if abs(y_min) > 1e-15:
                    new_y_min = y_min * 0.98
                    new_y_max = y_max * 1.02
                else:
                    new_y_min = -0.1
                    new_y_max = 0.1
            
            self.ax.set_ylim(new_y_min, new_y_max)
        
        # Set X-axis to show a scrolling window
        if len(self._x) > 0:
            x_max = self._x[-1]
            x_min = max(0, x_max - self._window_size)
            self.ax.set_xlim(x_min, x_max)
        
        self.draw_idle()

    def set_ylabel(self, label: str) -> None:
        self.ax.set_ylabel(label)
        self.draw_idle()
