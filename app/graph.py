from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class MetricGraphCanvas(FigureCanvas):
    def __init__(self, parent=None, width: float = 5, height: float = 3, dpi: int = 100):
        self.figure, self.axes = plt.subplots(figsize=(width, height), dpi=dpi)
        self.figure.patch.set_facecolor("#1e1e24")
        self.axes.set_facecolor("#151518")

        super().__init__(self.figure)
        self.setParent(parent)

        self.cpu_history = [0.0] * 30
        self.memory_history = [0.0] * 30
        self.axes.tick_params(colors="gold", labelsize=8)
        self.axes.grid(True, color="#333333", linestyle="--")
        self.axes.set_ylim(0, 100)
        self.axes.set_xlim(0, 29)
        self.cpu_line, = self.axes.plot(
            self.cpu_history, color="#e63946", label="CPU %", linewidth=2
        )
        self.memory_line, = self.axes.plot(
            self.memory_history, color="#4ea8de", label="Memory %", linewidth=2
        )
        self.axes.legend(
            loc="upper left",
            facecolor="#1e1e24",
            edgecolor="gold",
            labelcolor="white",
        )
        self.figure.tight_layout()

    def update_graph(self, cpu_percent: float, memory_percent: float) -> None:
        self.cpu_history = self.cpu_history[1:] + [cpu_percent]
        self.memory_history = self.memory_history[1:] + [memory_percent]
        self.cpu_line.set_ydata(self.cpu_history)
        self.memory_line.set_ydata(self.memory_history)
        self.draw_idle()
