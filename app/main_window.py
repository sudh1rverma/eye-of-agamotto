from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QStyle,
    QSystemTrayIcon,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
import psutil

from app.graph import MetricGraphCanvas
from app.process_manager import get_top_processes, terminate_process
from app.system_monitor import read_system_metrics


class EyeOfAgamotto(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eye of Agamotto - System Monitor")
        self.resize(750, 600)
        self.is_compact = False
        self._alert_is_active = False

        self._apply_style()
        self._create_widgets()
        self._configure_notifications()

        self.metrics_timer = QTimer(self)
        self.metrics_timer.timeout.connect(self.update_metrics)
        self.metrics_timer.start(1000)

        self.process_timer = QTimer(self)
        self.process_timer.timeout.connect(self.refresh_process_list)
        self.process_timer.start(5000)

        self.update_metrics()
        self.refresh_process_list()

    def _apply_style(self) -> None:
        self.setStyleSheet(
            
            """
            QMainWindow, QWidget { background-color: #1e1e24; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
            QLabel { font-size: 13px; color: #e0e0e0; }
            QLabel#Title { font-size: 22px; font-weight: bold; color: #ffb703; padding: 5px; }
            QProgressBar { border: 1px solid #ffb703; border-radius: 4px; text-align: center; background-color: #151518; color: white; }
            QProgressBar::chunk { background-color: #d62828; }
            QPushButton { background-color: #d62828; color: white; border: 1px solid #ffb703; border-radius: 4px; padding: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #b71c1c; }
            QPushButton#CompactBtn { background-color: #023e8a; }
            QPushButton#CompactBtn:hover { background-color: #0077b6; }
            QTableWidget { background-color: #151518; gridline-color: #ffb703; border: 1px solid #ffb703; color: white; }
            QHeaderView::section { background-color: #2b2d42; color: #ffb703; padding: 4px; border: 1px solid #151518; }
            QTabWidget::pane { border: 1px solid #ffb703; }
            QTabBar::tab { background: #2b2d42; padding: 8px 20px; color: #e0e0e0; }
            QTabBar::tab:selected { background: #151518; color: #ffb703; font-weight: bold; }
            QSpinBox { background-color: #151518; color: white; border: 1px solid #ffb703; padding: 3px; }
        """
        
        )

    def _create_widgets(self) -> None:
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)

        title_label = QLabel("Eye of Agamotto")
        title_label.setObjectName("Title")
        title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title_label)

        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.content_container)

        self.stats_widget = QWidget()
        stats_layout = QVBoxLayout(self.stats_widget)
        self.cpu_label, self.cpu_bar = self._make_metric_row("CPU Usage")
        self.memory_label, self.memory_bar = self._make_metric_row("Memory Usage")
        self.disk_label, self.disk_bar = self._make_metric_row("Disk Space Used")
        self.battery_label, self.battery_bar = self._make_metric_row("Battery Status")

        for label, bar in (
            (self.cpu_label, self.cpu_bar),
            (self.memory_label, self.memory_bar),
            (self.disk_label, self.disk_bar),
            (self.battery_label, self.battery_bar),
        ):
            stats_layout.addWidget(label)
            stats_layout.addWidget(bar)

        self.content_layout.addWidget(self.stats_widget)
        self.tabs = QTabWidget()
        self.content_layout.addWidget(self.tabs)

        self._create_dashboard_tab()
        self._create_process_tab()

        self.compact_button = QPushButton("Toggle Compact Mode")
        self.compact_button.setObjectName("CompactBtn")
        self.compact_button.clicked.connect(self.toggle_compact_mode)
        self.main_layout.addWidget(self.compact_button)

    @staticmethod
    def _make_metric_row(name: str):
        return QLabel(f"{name}: N/A"), QProgressBar()

    def _create_dashboard_tab(self) -> None:
        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_tab)
        self.graph_canvas = MetricGraphCanvas(self)
        dashboard_layout.addWidget(self.graph_canvas)

        alert_controls = QHBoxLayout()
        alert_controls.addWidget(QLabel("Alert Threshold %:"))
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(10, 95)
        self.threshold_spin.setValue(80)
        alert_controls.addWidget(self.threshold_spin)

        self.notify_check = QCheckBox("Enable Desktop Notifications")
        self.notify_check.setChecked(True)
        alert_controls.addWidget(self.notify_check)
        dashboard_layout.addLayout(alert_controls)
        self.tabs.addTab(dashboard_tab, "Multiverse Analytics")

    def _create_process_tab(self) -> None:
        process_tab = QWidget()
        process_layout = QVBoxLayout(process_tab)
        self.process_table = QTableWidget(0, 4)
        self.process_table.setHorizontalHeaderLabels(
            ["PID", "Application Name", "CPU %", "Memory %"]
        )
        self.process_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.process_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.process_table.setEditTriggers(QTableWidget.NoEditTriggers)
        process_layout.addWidget(self.process_table)

        self.banish_button = QPushButton("Banish Rogue Process")
        self.banish_button.clicked.connect(self.banish_process)
        process_layout.addWidget(self.banish_button)
        self.tabs.addTab(process_tab, "Rogue Entities")

    def _configure_notifications(self) -> None:
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_icon.setToolTip("Eye of Agamotto System Monitor")
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.show()
        else:
            self.notify_check.setEnabled(False)
            self.notify_check.setChecked(False)
            self.notify_check.setToolTip("Desktop notifications are unavailable in this session.")

    def update_metrics(self) -> None:
        metrics = read_system_metrics()
        self.cpu_label.setText(f"CPU Usage: {metrics.cpu_percent:.1f}%")
        self.cpu_bar.setValue(round(metrics.cpu_percent))
        self.memory_label.setText(f"Memory Usage: {metrics.memory_percent:.1f}%")
        self.memory_bar.setValue(round(metrics.memory_percent))
        self.disk_label.setText(f"Disk Space Used: {metrics.disk_percent:.1f}%")
        self.disk_bar.setValue(round(metrics.disk_percent))

        if metrics.battery_percent is None:
            self.battery_label.setText("Battery Status: N/A (No Battery or unavailable)")
            self.battery_bar.setValue(0)
            self.battery_label.show()
            self.battery_bar.hide()
        else:
            state = "Charging" if metrics.battery_plugged_in else "Discharging"
            self.battery_label.setText(
                f"Battery Status: {metrics.battery_percent:.1f}% ({state})"
            )
            self.battery_bar.setValue(round(metrics.battery_percent))
            self.battery_label.show()
            self.battery_bar.show()

        threshold = self.threshold_spin.value()
        self._set_bar_color(self.cpu_bar, metrics.cpu_percent >= threshold)
        self._set_bar_color(self.memory_bar, metrics.memory_percent >= threshold)
        self._set_bar_color(self.disk_bar, metrics.disk_percent >= threshold)
        self.graph_canvas.update_graph(metrics.cpu_percent, metrics.memory_percent)
        self._notify_if_needed(
            metrics.cpu_percent,
            metrics.memory_percent,
            metrics.disk_percent,
            threshold,
        )

    @staticmethod
    def _set_bar_color(progress_bar: QProgressBar, is_high: bool) -> None:
        color = "#d62828" if is_high else "#2a9d8f"
        progress_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")

    def _notify_if_needed(
        self,
        cpu_percent: float,
        memory_percent: float,
        disk_percent: float,
        threshold: int,
    ) -> None:
        high_metrics = []
        if cpu_percent >= threshold:
            high_metrics.append(f"CPU {cpu_percent:.1f}%")
        if memory_percent >= threshold:
            high_metrics.append(f"memory {memory_percent:.1f}%")
        if disk_percent >= threshold:
            high_metrics.append(f"disk {disk_percent:.1f}%")

        alert_is_active = bool(high_metrics)
        if alert_is_active and not self._alert_is_active and self.notify_check.isChecked():
            self.tray_icon.showMessage(
                "High system usage",
                f"Threshold {threshold}% reached: {', '.join(high_metrics)}",
                QSystemTrayIcon.Warning,
                5000,
            )
        self._alert_is_active = alert_is_active

    def refresh_process_list(self) -> None:
        processes = get_top_processes()
        self.process_table.setRowCount(len(processes))

        for row, process in enumerate(processes):
            pid_item = QTableWidgetItem(str(process.pid))
            pid_item.setData(Qt.UserRole, process.pid)
            pid_item.setData(Qt.UserRole + 1, process.create_time)
            self.process_table.setItem(row, 0, pid_item)
            self.process_table.setItem(row, 1, QTableWidgetItem(process.name))
            self.process_table.setItem(row, 2, QTableWidgetItem(f"{process.cpu_percent:.1f}%"))
            self.process_table.setItem(row, 3, QTableWidgetItem(f"{process.memory_percent:.1f}%"))

    def banish_process(self) -> None:
        row = self.process_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection Missing", "Select a process first.")
            return

        pid_item = self.process_table.item(row, 0)
        pid = pid_item.data(Qt.UserRole)
        create_time = pid_item.data(Qt.UserRole + 1)
        name = self.process_table.item(row, 1).text()

        confirm = QMessageBox.question(
            self,
            "Confirm Termination",
            f"Ask '{name}' (PID: {pid}) to stop? Unsaved work in that process may be lost.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            terminate_process(pid, create_time)
            QMessageBox.information(self, "Process Stopped", f"'{name}' stopped.")
            self.refresh_process_list()
        except psutil.Error as error:
            QMessageBox.critical(self, "Could Not Stop Process", str(error))
        except (PermissionError, RuntimeError) as error:
            QMessageBox.warning(self, "Could Not Stop Process", str(error))

    def toggle_compact_mode(self) -> None:
        self.is_compact = not self.is_compact
        if self.is_compact:
            self.tabs.hide()
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.resize(320, 240)
        else:
            self.tabs.show()
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.resize(750, 600)
        self.show()
