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
        
        self._x: List[float] = []
        self._y: List[float] = []
        (self._line,) = self.ax.plot([], [], linewidth=1.5)

        self.fig = fig
        
        # Y-axis limits (will be set after first few points)
        self._y_limits_set = False
        self._y_min = None
        self._y_max = None
        
        # Scrolling window settings
        self._window_size = 30.0  # Show last 30 seconds

    def clear(self) -> None:
        self._x.clear()
        self._y.clear()
        self._line.set_data([], [])
        self._y_limits_set = False
        self._y_min = None
        self._y_max = None
        self.ax.relim()
        self.ax.autoscale_view()
        self.draw_idle()

    def append_point(self, x: float, y: float) -> None:
        self._x.append(float(x))
        self._y.append(float(y))
        self._line.set_data(self._x, self._y)
        
        # After collecting ~10 points, set Y limits based on data range
        if not self._y_limits_set and len(self._y) >= 10:
            y_min = min(self._y)
            y_max = max(self._y)
            y_range = y_max - y_min
            
            # Add 10% padding on top and bottom
            if y_range > 0:
                padding = y_range * 0.1
                self._y_min = y_min - padding
                self._y_max = y_max + padding
            else:
                # If all values are the same, use ±10% of the value
                if abs(y_min) > 1e-15:
                    self._y_min = y_min * 0.9
                    self._y_max = y_max * 1.1
                else:
                    self._y_min = -1e-10
                    self._y_max = 1e-10
            
            self.ax.set_ylim(self._y_min, self._y_max)
            self._y_limits_set = True
        
        # Set X-axis to show a scrolling window
        if len(self._x) > 0:
            x_max = self._x[-1]
            x_min = max(0, x_max - self._window_size)
            self.ax.set_xlim(x_min, x_max)
        
        self.draw_idle()

    def set_ylabel(self, label: str) -> None:
        self.ax.set_ylabel(label)
        self.draw_idle()
