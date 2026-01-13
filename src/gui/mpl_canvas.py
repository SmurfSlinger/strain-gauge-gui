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
        self._x: List[float] = []
        self._y: List[float] = []
        (self._line,) = self.ax.plot([], [])

        self.fig = fig

    def clear(self) -> None:
        self._x.clear()
        self._y.clear()
        self._line.set_data([], [])
        self.ax.relim()
        self.ax.autoscale_view()
        self.draw_idle()

    def append_point(self, x: float, y: float) -> None:
        self._x.append(float(x))
        self._y.append(float(y))
        self._line.set_data(self._x, self._y)
        self.ax.relim()
        self.ax.autoscale_view()
        self.draw_idle()

    def set_ylabel(self, label: str) -> None:
        self.ax.set_ylabel(label)
        self.draw_idle()
