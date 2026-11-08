# Fixed runnable copy based on the uploaded V11_2_grouped.py
import csv
import json
import math
import queue
import re
import sys
import threading
import time
import traceback
import tempfile
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Deque, List, Optional, Sequence, Tuple

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None

try:
    from PySide6.QtCore import QTimer, Qt, QUrl, QPoint, QRectF
    from PySide6.QtGui import QColor, QFont, QKeySequence, QShortcut, QPixmap, QIcon, QPainter, QPen, QBrush, QDesktopServices
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QFileDialog,
        QFrame,
        QGroupBox,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMenuBar,
        QSpinBox,
        QMessageBox,
        QPushButton,
        QPlainTextEdit,
        QProgressBar,
        QScrollArea,
        QListWidget,
        QListWidgetItem,
        QInputDialog,
        QSizePolicy,
        QColorDialog,
        QAbstractItemView,
        QSplitter,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    QApplication = None

try:
    import matplotlib

    matplotlib.use("QtAgg")
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
except ImportError:
    FigureCanvas = None
    Figure = None


APP_TITLE = "Cosine Response Test Bench Controller"
APP_VERSION = "26.7"
APP_RELEASE_DATE = "27 March 2026"
APP_DEVELOPER = "Attila Preszter"
CHANGELOG_URL = "https://github.com/Nortcel/cosine-response-test-bench/releases"
ERROR_LOG_FILE = "cosine_bench_error.log"
SETTINGS_FILE = "cosine_bench_settings.json"
BAUD_RATE = 9600
MAX_POINTS = 101
MAX_COMPARE_SCANS = 8
READ_TIMEOUT = 0.2
POLARITY_HIGHER_IS_MORE = "Higher voltage = more light"

POLARITY_LOWER_IS_MORE = "Lower voltage = more light"

BUTTON_ACTIVE_STYLE = "QPushButton { background-color: #c9e8c9; border: 1px solid #73a973; border-radius: 4px; color: #163816; font-weight: 700; } QPushButton:disabled { background-color: #ececec; border: 1px solid #c9c9c9; border-radius: 4px; color: #9a9a9a; }"
BUTTON_INACTIVE_STYLE = "QPushButton { background-color: #b8b8b8; border: 1px solid #8f8f8f; border-radius: 4px; color: #2f2f2f; font-weight: 600; } QPushButton:disabled { background-color: #ececec; border: 1px solid #c9c9c9; border-radius: 4px; color: #9a9a9a; }"
BUTTON_DISABLED_STYLE = "QPushButton { background-color: #ececec; border: 1px solid #c9c9c9; border-radius: 4px; color: #9a9a9a; font-weight: 600; }"
BUTTON_MOVING_STYLE = "QPushButton { background-color: #f6d7a7; border: 1px solid #d4ad68; border-radius: 4px; color: #5d430d; font-weight: 600; } QPushButton:disabled { background-color: #ececec; border: 1px solid #c9c9c9; border-radius: 4px; color: #9a9a9a; }"
BUTTON_LASER_ON_STYLE = "QPushButton { background-color: #e39aa2; border: 1px solid #c96d7c; border-radius: 4px; color: #6f1020; font-weight: 700; } QPushButton:disabled { background-color: #ececec; border: 1px solid #c9c9c9; border-radius: 4px; color: #9a9a9a; }"
BUTTON_NEUTRAL_STYLE = "QPushButton { background-color: #f3f4f6; border: 1px solid #c4cad2; border-radius: 4px; color: #374151; font-weight: 600; } QPushButton:pressed { background-color: #e1e5ea; } QPushButton:disabled { background-color: #ececec; border: 1px solid #c9c9c9; border-radius: 4px; color: #9a9a9a; }"
RESET_BEST_BUTTON_STYLE = "QPushButton { background-color: #f3f4f6; border: 1px solid #c4cad2; border-radius: 4px; color: #374151; font-weight: 600; padding: 0 10px; } QPushButton:pressed { background-color: #e1e5ea; border-color: #9aa4b2; padding-top: 1px; padding-left: 11px; } QPushButton:disabled { background-color: #ececec; border: 1px solid #c9c9c9; border-radius: 4px; color: #9a9a9a; }"
BUTTON_PRESS_FEEDBACK_STYLE = RESET_BEST_BUTTON_STYLE
SOFTWARE_CHECK_BLUE = "#78BFFF"
SOFTWARE_CHECK_BLUE_HOVER = "#8DCCFF"
UI_ASSET_DIR = Path(tempfile.gettempdir()) / "cosine_bench_ui_assets"
UI_ASSET_DIR.mkdir(parents=True, exist_ok=True)
CHECK_TICK_ICON = UI_ASSET_DIR / "checkbox_tick_24_6.svg"
COMBO_ARROW_ICON = UI_ASSET_DIR / "combo_arrow_24_6.svg"
if not CHECK_TICK_ICON.exists():
    CHECK_TICK_ICON.write_text(
        "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"14\" height=\"14\" viewBox=\"0 0 14 14\"><path d=\"M3 7.2l2.2 2.4L11 4.3\" fill=\"none\" stroke=\"#ffffff\" stroke-width=\"2.1\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg>",
        encoding="utf-8",
    )
if not COMBO_ARROW_ICON.exists():
    COMBO_ARROW_ICON.write_text(
        "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"10\" height=\"6\" viewBox=\"0 0 10 6\"><path d=\"M1 1l4 4 4-4\" fill=\"none\" stroke=\"#5f6d7a\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"/></svg>",
        encoding="utf-8",
    )
APP_UI_STYLE = f"""
QCheckBox {{
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 13px;
    height: 13px;
    border: 1px solid #748292;
    border-radius: 2px;
    background: #ffffff;
}}
QCheckBox::indicator:unchecked:hover {{
    border-color: #637180;
    background: #f7fbff;
}}
QCheckBox::indicator:checked {{
    background: {SOFTWARE_CHECK_BLUE};
    border: 1px solid #63AFEA;
    image: url({CHECK_TICK_ICON.as_posix()});
}}
QCheckBox::indicator:checked:hover {{
    background: {SOFTWARE_CHECK_BLUE_HOVER};
    border-color: #63AFEA;
    image: url({CHECK_TICK_ICON.as_posix()});
}}
QComboBox {{
    border: 1px solid #9EA8B3;
    border-radius: 3px;
    background: #ffffff;
    padding: 1px 24px 1px 6px;
}}
QComboBox:hover {{
    border-color: #8A95A1;
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #AAB4BE;
    background: #f7f7f7;
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
}}
QComboBox::down-arrow {{
    image: url({COMBO_ARROW_ICON.as_posix()});
    width: 10px;
    height: 6px;
}}
QComboBox QAbstractItemView {{
    border: 1px solid #86919C;
    background: #ffffff;
    selection-background-color: #D7EEFF;
    selection-color: #111111;
    outline: 0;
}}
"""


WINDOW_GROUPBOX_STYLE = "QGroupBox { background-color: #f7f7f7; padding-top: 12px; margin-top: 8px; } QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px 0 3px; }"
WINDOW_FRAME_STYLE = "background-color: #f7f7f7;"


class EnvironmentGauge(QWidget):
    def __init__(self, min_value=0.0, max_value=100.0, normal_min=None, normal_max=None, units="", fill_colour="#64b5f6", parent=None):
        super().__init__(parent)
        self.min_value = float(min_value)
        self.max_value = float(max_value)
        self.normal_min = None if normal_min is None else float(normal_min)
        self.normal_max = None if normal_max is None else float(normal_max)
        self.units = units
        self.fill_colour = QColor(fill_colour)
        self.value = None
        self.setMinimumHeight(34)
        self.setMaximumHeight(38)
        self.setMinimumWidth(180)
        self.setMaximumWidth(16777215)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def setValueFloat(self, value):
        self.value = None if value is None else float(value)
        self.update()

    def _x_for_value(self, value, left, width):
        if self.max_value <= self.min_value:
            return left
        ratio = (value - self.min_value) / (self.max_value - self.min_value)
        ratio = max(0.0, min(1.0, ratio))
        return left + ratio * width

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        rect = self.rect()
        left = 12
        right = rect.width() - 12
        track_y = 12
        track_h = 8
        track_w = max(0, right - left)

        fm = painter.fontMetrics()
        tick_label_y = rect.height() - 1

        ticks = [
            (self.min_value, f"{int(self.min_value)}"),
            ((self.min_value + self.max_value) / 2.0, f"{int((self.min_value + self.max_value) / 2.0)}"),
            (self.max_value, f"{int(self.max_value)} {self.units}".rstrip()),
        ]

        painter.setPen(QPen(QColor("#a8a8a8"), 1))
        painter.setBrush(QBrush(QColor("#f5f5f5")))
        painter.drawRoundedRect(left, track_y, track_w, track_h, 4, 4)

        if self.value is not None:
            vx = self._x_for_value(self.value, left, track_w)
            fill_w = max(0, int(vx - left))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(self.fill_colour))
            painter.drawRoundedRect(left + 1, track_y + 1, max(0, fill_w - 1), track_h - 2, 3, 3)

        if self.normal_min is not None and self.normal_max is not None:
            n1 = self._x_for_value(self.normal_min, left, track_w)
            n2 = self._x_for_value(self.normal_max, left, track_w)
            band_x = int(min(n1, n2))
            band_w = int(abs(n2 - n1))
            painter.setPen(QPen(QColor(129, 199, 132, 170), 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(band_x, track_y + 1, band_w, track_h - 2, 3, 3)

        painter.setPen(QPen(QColor("#777777"), 1))
        for tick_val, _label in ticks:
            x = int(self._x_for_value(tick_val, left, track_w))
            painter.drawLine(x, track_y + track_h + 1, x, track_y + track_h + 4)

        if self.value is not None:
            vx = int(self._x_for_value(self.value, left, track_w))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor("#444444")))
            points = [
                (vx, track_y - 1),
                (vx - 4, track_y - 7),
                (vx + 4, track_y - 7),
            ]
            from PySide6.QtCore import QPoint
            painter.drawPolygon([QPoint(x, y) for x, y in points])

        painter.setPen(QPen(QColor("#666666"), 1))
        for tick_val, label in ticks:
            x = self._x_for_value(tick_val, left, track_w)
            label_w = fm.horizontalAdvance(label)
            label_x = int(x - label_w * 0.5)
            if tick_val == self.min_value:
                label_x = left - 2
            elif tick_val == self.max_value:
                label_x = right - label_w
            painter.drawText(label_x, tick_label_y, label)

        painter.end()


class AlignmentStrengthBar(QWidget):
    def __init__(self, min_value=0.0, max_value=5000.0, parent=None):
        super().__init__(parent)
        self.min_value = float(min_value)
        self.max_value = float(max_value)
        self.value = None
        self.best_value = None
        self.display_text = None
        self.inverted_appearance = False
        self.setMinimumHeight(32)
        self.setMaximumHeight(34)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def setRange(self, min_value, max_value):
        self.min_value = float(min_value)
        self.max_value = float(max_value)
        self.update()

    def setValue(self, value):
        self.value = None if value is None else float(value)
        self.update()

    def setFormat(self, text):
        self.display_text = text
        self.update()

    def setInvertedAppearance(self, inverted):
        self.inverted_appearance = bool(inverted)
        self.update()

    def setBestValue(self, best_value):
        self.best_value = None if best_value is None else float(best_value)
        self.update()

    def setValueData(self, value, best_value=None):
        self.value = None if value is None else float(value)
        self.best_value = None if best_value is None else float(best_value)
        self.update()

    def _x_for_value(self, value, left, width):
        if self.max_value <= self.min_value:
            return left
        ratio = (value - self.min_value) / (self.max_value - self.min_value)
        ratio = max(0.0, min(1.0, ratio))
        return left + ratio * width

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        rect = self.rect()
        left = 1
        top = 1
        width = max(0, rect.width() - 2)
        height = max(0, rect.height() - 2)

        painter.setPen(QPen(QColor('#777777'), 1))
        painter.setBrush(QBrush(QColor('#ffffff')))
        painter.drawRoundedRect(left, top, width, height, 4, 4)

        track_left = left + 2
        track_top = top + 2
        track_width = max(0, width - 4)
        track_height = max(0, height - 4)

        if self.value is not None:
            value_x = self._x_for_value(self.value, track_left, track_width)
            if self.inverted_appearance:
                fill_rect = QRectF(value_x, track_top, max(0.0, track_left + track_width - value_x), track_height)
            else:
                fill_rect = QRectF(track_left, track_top, max(0.0, value_x - track_left), track_height)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor('#ff8a00')))
            painter.drawRoundedRect(fill_rect, 3, 3)

        if self.best_value is not None:
            bx = int(self._x_for_value(self.best_value, track_left, track_width))
            painter.setPen(QPen(QColor('#000000'), 2))
            painter.drawLine(bx, track_top + 1, bx, track_top + track_height - 1)

        text_value = self.display_text if self.display_text is not None else ('-- V' if self.value is None else f'{self.value:.4f} V')
        painter.setPen(QPen(QColor('#111111'), 1))
        font = painter.font()
        font.setBold(True)
        font.setPointSize(max(10, font.pointSize()))
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, text_value)
        painter.end()


@dataclass
class ParsedState:
    mode: str = "Idle"
    temperature_c: Optional[float] = None
    humidity_percent: Optional[float] = None
    live_voltage_v: Optional[float] = None
    samples: int = 0
    interrupted: bool = False


@dataclass
class SamplePoint:
    index: int
    angle_deg: float
    voltage: float


@dataclass
class ScanRecord:
    label: str
    diode_model: str
    samples: list
    colour: str = "#ff5a1f"
    interrupted: bool = False


class SerialWorker:
    def __init__(self, on_line_callback: Callable[[str], None], on_status_callback: Callable[[str], None]):
        self.on_line_callback = on_line_callback
        self.on_status_callback = on_status_callback
        self.ser = None
        self.thread = None
        self.stop_event = threading.Event()
        self.write_lock = threading.Lock()

    def connect(self, port: str, baud_rate: int = BAUD_RATE):
        if serial is None:
            raise RuntimeError("pyserial is not installed. Install it with: pip install pyserial")
        self.disconnect(notify=False)
        self.stop_event.clear()
        self.ser = serial.Serial(port, baud_rate, timeout=READ_TIMEOUT)
        self.thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.thread.start()
        self.on_status_callback(f"Connected to {port} at {baud_rate} baud")

    def disconnect(self, notify: bool = True):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.thread = None
        if self.ser:
            try:
                if self.ser.is_open:
                    self.ser.close()
            except Exception:
                pass
        self.ser = None
        if notify:
            self.on_status_callback("Disconnected")

    def send(self, command: str):
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Serial port is not connected")
        data = (command.strip().upper() + "\n").encode("utf-8")
        with self.write_lock:
            self.ser.write(data)
            self.ser.flush()

    def _reader_loop(self):
        while not self.stop_event.is_set() and self.ser and self.ser.is_open:
            try:
                raw = self.ser.readline()
                if not raw:
                    continue
                line = raw.decode("utf-8", errors="replace").strip()
                if line:
                    self.on_line_callback(line)
            except Exception as exc:
                self.on_status_callback(f"Serial read error: {exc}")
                break


class MeasurementParser:
    voltage_pattern = re.compile(r"^Voltage\s*=\s*,?\s*([-+]?[0-9]+(?:\.[0-9]+)?)$", re.IGNORECASE)
    align_voltage_pattern = re.compile(r"^AlignVoltage\s*=\s*,?\s*([-+]?[0-9]+(?:\.[0-9]+)?)$", re.IGNORECASE)
    humidity_pattern = re.compile(r"^Humidity\s*=\s*,?\s*([-+]?[0-9]+(?:\.[0-9]+)?)$", re.IGNORECASE)
    temp_pattern = re.compile(r"^Temperature\s*=\s*,?\s*([-+]?[0-9]+(?:\.[0-9]+)?)$", re.IGNORECASE)
    angle_pattern = re.compile(r"^Angle\s*=\s*,?\s*([-+]?[0-9]+(?:\.[0-9]+)?)$", re.IGNORECASE)
    sample_pattern = re.compile(r"^Sample\s*=\s*,?\s*([0-9]+)$", re.IGNORECASE)

    def __init__(self, max_points: int = MAX_POINTS):
        self.max_points = max_points
        self.state = ParsedState()
        self.samples: List[SamplePoint] = []
        self.pending_angle: Optional[float] = None
        self.pending_index: Optional[int] = None
        self.scan_completed = False
        self.scan_history = []
        self.scan_counter = 0

    @property
    def angles(self) -> List[float]:
        return [s.angle_deg for s in self.samples]

    @property
    def voltages(self) -> List[float]:
        return [s.voltage for s in self.samples]

    def feed_line(self, line: str):
        low = line.lower()

        if "measurement started" in low:
            self.state.mode = "Measuring"
            self.state.interrupted = False
            self.scan_completed = False
            self.clear_measurement(preserve_history=True)
        elif "measurement complete" in low:
            self.state.mode = "Standby"
            self.scan_completed = True
        elif "free mode active" in low:
            self.state.mode = "Free"
        elif "returning to nullpoint" in low:
            self.state.mode = "Homing"
        elif "nullpoint reached" in low or "already at nullpoint" in low:
            self.state.mode = "Standby"
        elif "mode=standby" in low:
            self.state.mode = "Standby"
        elif "mode=measuring" in low:
            self.state.mode = "Measuring"
        elif "mode=free" in low:
            self.state.mode = "Free"
        elif "mode=homing" in low:
            self.state.mode = "Homing"

        if "right end sensor triggered" in low or "measurement stopped" in low:
            self.state.interrupted = True

        hum_match = self.humidity_pattern.search(line)
        if hum_match:
            self.state.humidity_percent = float(hum_match.group(1))

        temp_match = self.temp_pattern.search(line)
        if temp_match:
            self.state.temperature_c = float(temp_match.group(1))

        align_match = self.align_voltage_pattern.search(line)
        if align_match:
            self.state.live_voltage_v = float(align_match.group(1))
            return

        if line.startswith("Config:"):
            return

        angle_match = self.angle_pattern.search(line)
        if angle_match:
            self.pending_angle = float(angle_match.group(1))

        sample_match = self.sample_pattern.search(line)
        if sample_match:
            self.pending_index = int(sample_match.group(1)) - 1

        volt_match = self.voltage_pattern.search(line)
        if volt_match and self.state.samples < self.max_points:
            voltage = float(volt_match.group(1))
            self.state.live_voltage_v = voltage
            index = self.pending_index if self.pending_index is not None else self.state.samples
            angle = self.pending_angle if self.pending_angle is not None else self.angle_for_sample(index, self.max_points)
            self.samples.append(SamplePoint(index=index, angle_deg=angle, voltage=voltage))
            self.state.samples += 1
            self.pending_angle = None
            self.pending_index = None

    @staticmethod
    def angle_for_sample(index: int, max_points: int = MAX_POINTS) -> float:
        if max_points <= 1:
            return 0.0
        return -90.0 + (180.0 * index / (max_points - 1))

    def archive_current_scan(self, label="Previous scan", diode_model="", colour="#ff5a1f"):
        if self.samples:
            self.scan_history.append(
                ScanRecord(
                    label=label,
                    diode_model=diode_model,
                    samples=[SamplePoint(index=s.index, angle_deg=s.angle_deg, voltage=s.voltage) for s in self.samples],
                    colour=colour,
                    interrupted=self.state.interrupted,
                )
            )
            if len(self.scan_history) > MAX_COMPARE_SCANS:
                self.scan_history = self.scan_history[-MAX_COMPARE_SCANS:]

    def clear_measurement(self, preserve_history: bool = True):
        self.samples = []
        self.state.samples = 0
        self.pending_angle = None
        self.pending_index = None
        self.scan_completed = False
        if not preserve_history:
            self.scan_history = []
            self.scan_counter = 0

    def ideal_cosine_curve(self, point_count: int = MAX_POINTS) -> Tuple[List[float], List[float]]:
        angles = []
        values = []
        if point_count <= 1:
            return [0.0], [1.0]
        for i in range(point_count):
            angle = self.angle_for_sample(i, point_count)
            angles.append(angle)
            values.append(max(0.0, math.cos(math.radians(angle))))
        return angles, values

    def _dark_offset(self, polarity_mode: str) -> float:
        if not self.samples:
            return 0.0
        edge_values = [sample.voltage for sample in self.samples if abs(sample.angle_deg) >= 85.0]
        if edge_values:
            return sum(edge_values) / len(edge_values)
        if polarity_mode == POLARITY_LOWER_IS_MORE:
            return max(sample.voltage for sample in self.samples)
        return min(sample.voltage for sample in self.samples)

    def _reference_voltage(self, polarity_mode: str) -> float:
        if not self.samples:
            return 1.0
        centre_values = [sample.voltage for sample in self.samples if abs(sample.angle_deg) <= 2.0]
        if centre_values:
            return sum(centre_values) / len(centre_values)
        if polarity_mode == POLARITY_LOWER_IS_MORE:
            return min(sample.voltage for sample in self.samples)
        return max(sample.voltage for sample in self.samples)

    def corrected_voltages(self, polarity_mode: str) -> List[float]:
        if not self.samples:
            return []
        dark = self._dark_offset(polarity_mode)
        corrected: List[float] = []
        for sample in self.samples:
            if polarity_mode == POLARITY_LOWER_IS_MORE:
                corrected.append(max(0.0, dark - sample.voltage))
            else:
                corrected.append(max(0.0, sample.voltage - dark))
        return corrected

    def normalised_voltages(self, polarity_mode: str, samples: Optional[List[SamplePoint]] = None) -> List[float]:
        source_samples = self.samples if samples is None else samples
        if not source_samples:
            return []
        original_samples = self.samples
        if samples is not None:
            self.samples = source_samples
        try:
            dark = self._dark_offset(polarity_mode)
            reference_voltage = self._reference_voltage(polarity_mode)
            if polarity_mode == POLARITY_LOWER_IS_MORE:
                reference = max(dark - reference_voltage, 1e-9)
            else:
                reference = max(reference_voltage - dark, 1e-9)
            return [max(0.0, min(1.2, corrected / reference)) for corrected in self.corrected_voltages(polarity_mode)]
        finally:
            if samples is not None:
                self.samples = original_samples

    def calculate_rmse(self, polarity_mode: str) -> Optional[float]:
        if not self.samples:
            return None
        measured = self.normalised_voltages(polarity_mode)
        errors = []
        for angle, value in zip(self.angles, measured):
            if abs(angle) <= 80.0:
                ideal = max(0.0, math.cos(math.radians(angle)))
                errors.append((value - ideal) ** 2)
        if not errors:
            return None
        return math.sqrt(sum(errors) / len(errors))

    def calculate_symmetry_error(self, polarity_mode: str) -> Optional[float]:
        if len(self.samples) < 3:
            return None
        measured = self.normalised_voltages(polarity_mode)
        by_angle = {round(a, 4): v for a, v in zip(self.angles, measured)}
        errors = []
        for angle in self.angles:
            if angle < 0:
                key = round(angle, 4)
                partner = round(-angle, 4)
                if key in by_angle and partner in by_angle:
                    errors.append(abs(by_angle[key] - by_angle[partner]))
        if not errors:
            return None
        return sum(errors) / len(errors)

    def raw_voltage_ticks(self, polarity_mode: str, samples: Optional[List[SamplePoint]] = None, norm_ticks: Optional[List[float]] = None) -> List[Tuple[float, float]]:
        source_samples = self.samples if samples is None else samples
        if not source_samples:
            return []
        norm_ticks = norm_ticks or [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        original_samples = self.samples
        if samples is not None:
            self.samples = source_samples
        try:
            dark = self._dark_offset(polarity_mode)
            reference_voltage = self._reference_voltage(polarity_mode)
            if polarity_mode == POLARITY_LOWER_IS_MORE:
                scale = max(dark - reference_voltage, 1e-9)
                return [(tick, dark - tick * scale) for tick in norm_ticks]
            scale = max(reference_voltage - dark, 1e-9)
            return [(tick, dark + tick * scale) for tick in norm_ticks]
        finally:
            if samples is not None:
                self.samples = original_samples


    def draw_plot(self, ax, diode_model: str, polarity_mode: str, show_ideal: bool = True):
        if ax is None:
            return
        ax.clear()
        ax.set_title(f"Cosine response of {diode_model}" if diode_model else "Cosine response")
        ax.set_xlabel("Angle of Incidence (°)")
        ax.set_ylabel("Normalised Response (−)")
        ax.set_xlim(-100, 100)
        ax.set_ylim(0, 1.05)
        ax.grid(True, linestyle=(0, (1, 4)), linewidth=0.8)
        ax.axvline(0, linestyle="--", linewidth=1.0, color="#5fa3e3")

        if show_ideal:
            ideal_x, ideal_y = self.ideal_cosine_curve()
            ax.plot(ideal_x, ideal_y, label="Ideal Cosine (cos θ)", linewidth=2.0, color="#1f77b4")

        if self.samples:
            angles = [s.angle_deg for s in self.samples]
            norm = self.normalised_voltages(polarity_mode)
            ax.plot(angles, norm, marker="o", linewidth=1.2, markersize=3.2, color="#ff5a1f", label="Measured")

        if ax.lines:
            ax.legend(loc="upper left", fontsize=8)

    def save_plot(self, output_path: str, diode_model: str, polarity_mode: str, show_ideal: bool = True):
        if Figure is None:
            raise RuntimeError("matplotlib is not installed")
        fig = Figure(figsize=(10, 6), dpi=120)
        ax = fig.add_subplot(111)
        self.draw_plot(ax, diode_model, polarity_mode, show_ideal=show_ideal)
        fig.tight_layout()
        fig.savefig(output_path)

    def save_csv(self, output_path: str, diode_model: str, polarity_mode: str, notes: str = "", metadata: Optional[dict] = None):
        path = Path(output_path)
        metadata = metadata or {}

        scans = []
        for idx, rec in enumerate(self.scan_history, start=1):
            scans.append((rec.label or f"Scan {idx}", rec.samples))
        if self.samples:
            scans.append(("Current scan", self.samples))

        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["metadata", "value"])
            writer.writerow(["diode_model", diode_model])
            writer.writerow(["signal_polarity", polarity_mode])
            writer.writerow(["measurement_notes", notes])
            writer.writerow(["operator", metadata.get("operator", "")])
            writer.writerow(["diode_type", metadata.get("diode_type", "")])
            writer.writerow(["diffuser_used", metadata.get("diffuser_used", "")])
            writer.writerow(["bench_configuration", metadata.get("bench_configuration", "")])
            writer.writerow(["test_id", metadata.get("test_id", "")])
            writer.writerow(["firmware_version", metadata.get("firmware_version", "")])
            writer.writerow(["scan_duration_s", metadata.get("scan_duration_s", "")])
            writer.writerow(["scan_status", metadata.get("scan_status", "")])
            writer.writerow([])
            headers = []
            for label, _samples in scans:
                headers.extend([f"{label} angle_deg", f"{label} voltage_v", f"{label} normalised_v"])
            writer.writerow(headers)
            max_len = max((len(samps) for _, samps in scans), default=0)
            for row_idx in range(max_len):
                row = []
                for _label, samps in scans:
                    if row_idx < len(samps):
                        s = samps[row_idx]
                        norm_values = self.normalised_voltages(polarity_mode, samps)
                        norm = norm_values[row_idx] if row_idx < len(norm_values) else 0.0
                        row.extend([f"{s.angle_deg:.6f}", f"{s.voltage:.6f}", f"{norm:.6f}"])
                    else:
                        row.extend(["", "", ""])
                writer.writerow(row)


class BenchMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1600, 920)
        self.setMinimumSize(1200, 700)

        self.setStyleSheet(APP_UI_STYLE)
        self._startup_geometry_applied = False
        self.resolution_status_label: Optional[QLabel] = None

        self.message_queue: "queue.Queue[Tuple[str, str]]" = queue.Queue()
        self.parser = MeasurementParser()
        self.worker = SerialWorker(self._queue_line, self._queue_status)
        self.connected = False
        self.control_buttons: dict[str, QPushButton] = {}
        self.alignment_history: Deque[float] = deque(maxlen=160)
        self.best_alignment_voltage: Optional[float] = None
        self.best_reset_pending = False
        self.last_saved_file: Optional[str] = None
        self.scan_start_monotonic: Optional[float] = None
        self.last_scan_duration_s: Optional[float] = None
        self.current_scan_status = "Ready"
        self.laser_manual_on = False
        self.position_home_state = "inactive"
        self.position_end_state = "inactive"
        self.home_stop_guard_armed = False
        self.scan_visibility = {}
        self.last_scan_finished_at = None
        self.scan_palette = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#a65628", "#f781bf", "#17becf"]
        self.graph1_options = {"ideal": True, "current": True, "mirror": False, "grid": True, "error_band": False, "mode": "Normalised"}
        self.graph2_options = {"ideal": True, "current": True, "grid": True, "error_band": False, "mode": "Normalised"}
        self.current_scan_label = "Current scan"
        self._last_firmware_version = "--"
        self._last_board_name = "--"
        self._last_build_info = "--"
        self.scan_visibility = {}
        self.main_plot_splitter = None
        self.graph_column_splitter = None
        self.compare_scan_list_widget = None
        self.compare_panel_title_label = None
        self.rename_scan_button = None
        self.delete_scan_button = None
        self.graph1_export_png_check = None
        self.graph1_export_csv_check = None
        self.graph1_export_button = None
        self.graph1_export_frame = None
        self.graph1_export_toggle_button = None
        self.graph2_export_png_check = None
        self.graph2_export_csv_check = None
        self.graph2_export_avg_csv_check = None
        self.graph2_export_button = None
        self.graph2_export_frame = None
        self.graph2_export_toggle_button = None
        self.g1_ideal_check = None
        self.g1_current_check = None
        self.g1_mirror_check = None
        self.g1_grid_check = None
        self.g1_error_band_check = None
        self.g1_mode_combo = None
        self.g2_ideal_check = None
        self.g2_grid_check = None
        self.g2_error_band_check = None
        self.g2_mode_combo = None
        self.error_export_png_check = None
        self.error_export_csv_check = None
        self.error_export_button = None
        self.error_export_frame = None
        self.error_export_toggle_button = None
        self.clear_scans_button = None
        self.measurement_count_combo = None
        self.series_active = False
        self.series_total = 1
        self.series_index = 0
        self.pending_auto_restart = False
        self.pending_sequence_label = None
        self.current_scan_archived = False
        self.home_stop_guard_armed = False
        self.series_compare_mode = False
        self.best_reset_baseline: Optional[float] = None
        self.log_paused = False
        self.laser_manual_on = False

        self.port_combo: Optional[QComboBox] = None
        self.connect_button: Optional[QPushButton] = None
        self.controls_status_label: Optional[QLabel] = None
        self.status_label: Optional[QLabel] = None
        self.device_model_label: Optional[QLabel] = None
        self.device_port_label: Optional[QLabel] = None
        self.device_hwid_label: Optional[QLabel] = None
        self.device_manufacturer_label: Optional[QLabel] = None
        self.device_firmware_label: Optional[QLabel] = None
        self.device_connected_at_label: Optional[QLabel] = None
        self._connected_port_info = None
        self._connected_at_text = "--"
        self.mode_label: Optional[QLabel] = None
        self.temp_label: Optional[QLabel] = None
        self.temp_bar: Optional[QProgressBar] = None
        self.humidity_label: Optional[QLabel] = None
        self.humidity_bar: Optional[QProgressBar] = None
        self.samples_label: Optional[QLabel] = None
        self.progress_bar: Optional[QProgressBar] = None
        self.scan_progress_label: Optional[QLabel] = None
        self.rmse_label: Optional[QLabel] = None
        self.symmetry_label: Optional[QLabel] = None
        self.alignment_scale_label: Optional[QLabel] = None
        self.alignment_bar: Optional[QProgressBar] = None
        self.export_preview_label: Optional[QLabel] = None
        self.measurement_setup_summary_label: Optional[QLabel] = None
        self.measurement_setup_button: Optional[QPushButton] = None
        self.measurement_setup_dialog: Optional[QDialog] = None
        self.measurement_setup_form_widget: Optional[QWidget] = None
        self.measurement_setup_form_layout = None
        self.motion_control_summary_label: Optional[QLabel] = None
        self.motion_control_button: Optional[QPushButton] = None
        self.motion_control_dialog: Optional[QDialog] = None
        self.motion_control_form_widget: Optional[QWidget] = None
        self.motion_control_form_layout = None
        self.output_folder_edit: Optional[QLineEdit] = None
        self.diode_model_edit: Optional[QLineEdit] = None
        self.notes_edit: Optional[QLineEdit] = None
        self.scan_speed_spin: Optional[QSpinBox] = None
        self.return_speed_spin: Optional[QSpinBox] = None
        self.polarity_combo: Optional[QComboBox] = None
        self.log_box: Optional[QPlainTextEdit] = None
        self.canvas: Optional[FigureCanvas] = None
        self.figure: Optional[Figure] = None
        self.ax = None
        self.alignment_canvas: Optional[FigureCanvas] = None
        self.alignment_figure: Optional[Figure] = None
        self.alignment_ax = None
        self.compare_canvas = None
        self.trend_live_checkbox = None
        self.compare_figure = None
        self.compare_ax = None
        self.error_canvas = None
        self.main_plot_splitter = None
        self.content_splitter = None
        self.left_content_panel = None
        self._main_right_ax = None

        self._build_ui()
        self._apply_compact_top_layout()
        self._polish_button_styles()
        self._refresh_ports()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._process_queue)
        self.timer.start(100)
        QTimer.singleShot(250, self._maybe_show_update_popup)

    def _settings_path(self) -> Path:
        return Path(__file__).resolve().parent / SETTINGS_FILE

    def _load_json_settings_data(self) -> dict:
        path = self._settings_path()
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_json_settings_data(self, data: dict) -> None:
        path = self._settings_path()
        try:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass


    def _set_export_panel_visibility(self, panel_name: str, visible: bool):
        frame = getattr(self, f"{panel_name}_export_frame", None)
        button = getattr(self, f"{panel_name}_export_toggle_button", None)
        if frame is not None:
            frame.setVisible(visible)
        if button is not None:
            button.setText("Hide export" if visible else "Export")

    def _toggle_export_panel(self, panel_name: str):
        button = getattr(self, f"{panel_name}_export_toggle_button", None)
        if button is not None:
            self._show_export_popup(panel_name, button)

    def _show_export_popup(self, panel_name: str, anchor_button: QPushButton):
        dialog = QDialog(self, Qt.Popup)
        dialog.setWindowTitle("Export")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)
        title = QLabel("Export")
        title.setStyleSheet("font-size: 11px; font-weight: 600;")
        layout.addWidget(title)

        def add_check(label_text: str, checked: bool):
            cb = QCheckBox(label_text)
            cb.setChecked(checked)
            layout.addWidget(cb)
            return cb

        if panel_name == "graph1":
            png_cb = add_check("Graph (png)", self.graph1_export_png_check.isChecked())
            csv_cb = add_check("Scan Data (csv)", self.graph1_export_csv_check.isChecked())
            action = QPushButton("Export scan")
            action.clicked.connect(lambda: (self.graph1_export_png_check.setChecked(png_cb.isChecked()), self.graph1_export_csv_check.setChecked(csv_cb.isChecked()), dialog.accept(), self._export_graph1_selected()))
        elif panel_name == "graph2":
            png_cb = add_check("Graph (png)", self.graph2_export_png_check.isChecked())
            csv_cb = add_check("Scan Data (csv)*", self.graph2_export_csv_check.isChecked())
            avg_cb = add_check("Average Scan Data (csv)", self.graph2_export_avg_csv_check.isChecked())
            note = QLabel("*all displayed data")
            note.setStyleSheet("font-size: 9px; color: #666666;")
            layout.addWidget(note)
            action = QPushButton("Export scan")
            action.clicked.connect(lambda: (self.graph2_export_png_check.setChecked(png_cb.isChecked()), self.graph2_export_csv_check.setChecked(csv_cb.isChecked()), self.graph2_export_avg_csv_check.setChecked(avg_cb.isChecked()), dialog.accept(), self._export_graph2_selected()))
        else:
            png_cb = add_check("Graph (png)", self.error_export_png_check.isChecked())
            csv_cb = add_check("Scan Data (csv)", self.error_export_csv_check.isChecked())
            action = QPushButton("Export scan")
            action.clicked.connect(lambda: (self.error_export_png_check.setChecked(png_cb.isChecked()), self.error_export_csv_check.setChecked(csv_cb.isChecked()), dialog.accept(), self._export_error_selected()))

        action.setMinimumHeight(24)
        layout.addWidget(action)
        dialog.adjustSize()
        popup_size = dialog.sizeHint()
        anchor_top_left = anchor_button.mapToGlobal(anchor_button.rect().topLeft())
        pos = anchor_top_left - QPoint(0, popup_size.height() + 4)
        screen = QApplication.screenAt(anchor_top_left)
        if screen is not None:
            available = screen.availableGeometry()
            if pos.y() < available.top():
                pos = anchor_button.mapToGlobal(anchor_button.rect().bottomLeft()) + QPoint(0, 4)
            if pos.x() + popup_size.width() > available.right():
                pos.setX(max(available.left(), available.right() - popup_size.width()))
            if pos.x() < available.left():
                pos.setX(available.left())
        dialog.move(pos)
        dialog.exec()

    def _update_measurement_setup_summary(self):
        if self.measurement_setup_summary_label is None:
            return
        diode_model = self.diode_model_edit.text().strip() if self.diode_model_edit is not None else ""
        diode_type = self.diode_type_edit.text().strip() if hasattr(self, "diode_type_edit") and self.diode_type_edit is not None else ""
        diffuser_used = self.diffuser_edit.text().strip() if hasattr(self, "diffuser_edit") and self.diffuser_edit is not None else ""
        bench_config = self.bench_config_edit.text().strip() if hasattr(self, "bench_config_edit") and self.bench_config_edit is not None else ""
        test_id = self.test_id_edit.text().strip() if hasattr(self, "test_id_edit") and self.test_id_edit is not None else ""
        operator = self.operator_edit.text().strip() if hasattr(self, "operator_edit") and self.operator_edit is not None else ""
        output_folder = self.output_folder_edit.text().strip() if self.output_folder_edit is not None else ""
        summary_html = (
            "<table cellspacing='0' cellpadding='0' style='font-size:11px; color:#333333;'>"
            f"<tr><td style='padding-right:12px;'><b>Diode Model:</b> {diode_model or '--'}</td><td><b>Bench Config:</b> {bench_config or '--'}</td></tr>"
            f"<tr><td style='padding-right:12px;'><b>Diode Type:</b> {diode_type or '--'}</td><td><b>Test ID:</b> {test_id or '--'}</td></tr>"
            f"<tr><td style='padding-right:12px;'><b>Diffuser Used:</b> {diffuser_used or '--'}</td><td><b>Operator:</b> {operator or '--'}</td></tr>"
            "</table>"
        )
        self.measurement_setup_summary_label.setText(summary_html)
        self.measurement_setup_summary_label.setToolTip(output_folder or "Measurement setup summary")

    def _update_motion_control_summary(self):
        if self.motion_control_summary_label is None:
            return
        scan_speed = self.scan_speed_spin.value() if self.scan_speed_spin is not None else 0
        return_speed = self.return_speed_spin.value() if self.return_speed_spin is not None else 0
        polarity = self.polarity_combo.currentText().strip() if self.polarity_combo is not None else "--"
        summary_html = (
            f"<b>Scan:</b> {scan_speed} µs    <b>Return:</b> {return_speed} µs<br>"
            f"<b>Polarity:</b> {polarity or '--'}"
        )
        self.motion_control_summary_label.setText(summary_html)
        self.motion_control_summary_label.setToolTip("Motion control summary")

    def _close_measurement_setup_dialog(self):
        if self.measurement_setup_dialog is not None:
            self.measurement_setup_dialog.accept()

    def _show_measurement_setup_dialog(self):
        if self.measurement_setup_form_widget is None:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Measurement Setup")
        dialog.setMinimumWidth(820)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        self.measurement_setup_form_widget.setParent(dialog)
        self.measurement_setup_form_widget.setVisible(True)
        layout.addWidget(self.measurement_setup_form_widget)
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        self.measurement_setup_dialog = dialog
        dialog.exec()
        if self.measurement_setup_form_layout is not None:
            self.measurement_setup_form_widget.setParent(self)
            self.measurement_setup_form_layout.addWidget(self.measurement_setup_form_widget)
            self.measurement_setup_form_widget.setVisible(False)
        self.measurement_setup_dialog = None
        self._update_measurement_setup_summary()
        self._update_motion_control_summary()

    def _show_motion_control_dialog(self):
        if self.motion_control_form_widget is None:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Motion Control")
        dialog.setMinimumWidth(640)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        self.motion_control_form_widget.setParent(dialog)
        self.motion_control_form_widget.setVisible(True)
        layout.addWidget(self.motion_control_form_widget)
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        self.motion_control_dialog = dialog
        dialog.exec()
        if self.motion_control_form_layout is not None:
            self.motion_control_form_widget.setParent(self)
            self.motion_control_form_layout.addWidget(self.motion_control_form_widget)
            self.motion_control_form_widget.setVisible(False)
        self.motion_control_dialog = None
        self._update_motion_control_summary()

    def _apply_compact_top_layout(self):
        compact_font = QFont()
        compact_font.setPointSize(9)
        for group in self.findChildren(QGroupBox):
            group.setFont(compact_font)
            layout = group.layout()
            if layout is not None:
                layout.setContentsMargins(4, 4, 4, 4)
                layout.setSpacing(3)
                if hasattr(layout, "setVerticalSpacing"):
                    layout.setVerticalSpacing(2)
                if hasattr(layout, "setHorizontalSpacing"):
                    layout.setHorizontalSpacing(6)
        for button in self.findChildren(QPushButton):
            if button.text() in {"Start Scan", "Stop Scan", "Free Measure"}:
                button.setMinimumHeight(25)
            elif button.text() in {"Edit setup", "Export", "Hide export", "Hide Test Bench Settings", "Show Test Bench Settings"}:
                button.setMinimumHeight(21)
            else:
                button.setMinimumHeight(21)
        for edit in self.findChildren(QLineEdit):
            edit.setMinimumHeight(21)
        for edit in self.findChildren(QComboBox):
            edit.setMinimumHeight(21)
        for edit in self.findChildren(QSpinBox):
            edit.setMinimumHeight(21)

    def _polish_button_styles(self):
        radius = "4px"
        default_border = "#9a9a9a"
        for button in self.findChildren(QPushButton):
            existing = button.styleSheet() or ""
            if "border-radius" not in existing:
                existing = (existing + f" border-radius: {radius};").strip()
            if "background-color" not in existing and "border:" not in existing:
                existing = (existing + f" border: 1px solid {default_border};").strip()
            elif "background-color" not in existing and "border:" in existing and "#d" not in existing:
                pass
            button.setStyleSheet(existing)

        uniform = [
            getattr(self, "free_measure_button", None),
            getattr(self, "stop_live_button", None),
            getattr(self, "reset_best_button", None),
        ]
        styles = {
            self.free_measure_button: BUTTON_ACTIVE_STYLE,
            self.stop_live_button: BUTTON_DISABLED_STYLE,
            self.reset_best_button: RESET_BEST_BUTTON_STYLE,
        }
        for btn in uniform:
            if btn is not None:
                btn.setMinimumHeight(24)
                btn.setMaximumWidth(96)
                btn.setMinimumWidth(96)
                btn.setStyleSheet(styles[btn])

        pressed_feedback_buttons = [
            getattr(self, "refresh_button", None),
            getattr(self, "connect_button", None),
            getattr(self, "measurement_setup_button", None),
            getattr(self, "motion_control_button", None),
            getattr(self, "clear_plot_button", None),
            getattr(self, "clear_session_button", None),
            getattr(self, "browse_output_folder_button", None),
            getattr(self, "motion_preset_slow_button", None),
            getattr(self, "motion_preset_standard_button", None),
            getattr(self, "motion_preset_fast_button", None),
            getattr(self, "motion_read_speeds_button", None),
            getattr(self, "motion_apply_speeds_button", None),
            getattr(self, "motion_default_speeds_button", None),
        ]
        for btn in pressed_feedback_buttons:
            if btn is not None:
                btn.setStyleSheet(BUTTON_PRESS_FEEDBACK_STYLE)


    def _make_panel_frame(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setLineWidth(1)
        return frame

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Save CSV", self._save_csv)
        file_menu.addAction("Save PNG", self._save_png)
        file_menu.addAction("Export report set", self._export_report_set)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Read speeds", self._request_speed_settings)
        tools_menu.addAction("Apply speeds", self._apply_speed_settings)
        tools_menu.addAction("Show log", self._show_log_panel)
        tools_menu.addAction("Clear log", self._clear_log)
        tools_menu.addAction("Clear session", self._clear_session)
        tools_menu.addAction("Settings", self._show_settings_dialog)
        tools_menu.addAction("Reset all settings", self._reset_all_settings)

        help_menu = menubar.addMenu("Help")
        help_menu.addAction("How to use", self._show_help_dialog)
        help_menu.addAction(f"What's new (V{APP_VERSION})", self._show_whats_new_dialog)
        help_menu.addAction("Full changelog", self._open_full_changelog)
        help_menu.addAction("About", self._show_about_dialog)

        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(3, 0, 3, 3)
        main_layout.setSpacing(1)
        menubar.setStyleSheet("QMenuBar { padding-top: 0px; padding-bottom: 0px; margin: 0px; } QMenuBar::item { padding: 3px 8px; margin: 0px; }")

        header_container = QWidget()
        header_container.setStyleSheet("background-color: #f7f7f7;")
        header_container.setMinimumHeight(30)
        header_row = QHBoxLayout(header_container)
        header_row.setContentsMargins(8, 2, 8, 2)
        header_row.setSpacing(2)
        header_row.setAlignment(Qt.AlignVCenter)
        title_spacer_left = QWidget()
        title_spacer_left.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_row.addWidget(title_spacer_left, 1)
        title_label = QLabel(APP_TITLE)
        title_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        title_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        title_label.setMinimumHeight(28)
        title_label.setStyleSheet("font-size: 20px; font-weight: 700; padding: 0px; margin: 0px;")
        header_row.addWidget(title_label, 0, Qt.AlignVCenter)
        title_spacer_right = QWidget()
        title_spacer_right.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_row.addWidget(title_spacer_right, 1)
        self.header_version_label = QLabel(f"V{APP_VERSION}")
        self.header_version_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.header_version_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.header_version_label.setMinimumHeight(28)
        self.header_version_label.setStyleSheet("font-size: 11px; color: #555555; font-weight: 600; padding-right: 2px; margin: 0px;")
        header_row.addWidget(self.header_version_label, 0, Qt.AlignLeft | Qt.AlignVCenter)
        main_layout.addWidget(header_container, 0)

        self.operator_edit = QLineEdit()
        self.diode_type_edit = QLineEdit()
        self.diffuser_edit = QLineEdit()
        self.bench_config_edit = QLineEdit()
        self.test_id_edit = QLineEdit()
        self.diode_model_edit = QLineEdit()
        self.diode_model_edit.textChanged.connect(self._on_metadata_changed)
        self.export_preview_label = QLabel(self._suggest_export_basename())
        self.export_preview_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Optional notes for this scan")
        self.notes_edit.textChanged.connect(self._on_metadata_changed)
        self.output_folder_edit = QLineEdit(str(Path.cwd()))
        self.output_folder_edit.textChanged.connect(self._on_metadata_changed)
        connection_device_group = QGroupBox("Connection and Device")
        connection_device_group.setStyleSheet(WINDOW_GROUPBOX_STYLE)
        connection_device_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        connection_device_layout = QVBoxLayout(connection_device_group)
        connection_device_layout.setContentsMargins(8, 8, 8, 8)
        connection_device_layout.setSpacing(6)

        connection_row = QGridLayout()
        connection_row.setHorizontalSpacing(6)
        connection_row.setVerticalSpacing(4)
        connection_row.addWidget(QLabel("Serial port"), 0, 0)
        self.port_combo = QComboBox()
        self.port_combo.setToolTip("Select the COM port used by the test bench controller")
        self.port_combo.setMinimumWidth(150)
        connection_row.addWidget(self.port_combo, 0, 1)
        self.refresh_button = QPushButton("Refresh")
        refresh_button = self.refresh_button
        refresh_button.setMinimumHeight(24)
        refresh_button.clicked.connect(self._refresh_ports)
        connection_row.addWidget(refresh_button, 0, 2)
        self.connect_button = QPushButton("Connect")
        self.connect_button.setToolTip("Connect or disconnect the software from the test bench controller")
        self.connect_button.setMinimumHeight(24)
        self.connect_button.clicked.connect(self._toggle_connection)
        connection_row.addWidget(self.connect_button, 0, 3)
        self.status_label = QLabel("○ Disconnected")
        self.status_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.status_label.setStyleSheet("color: #666666;")
        connection_row.addWidget(self.status_label, 1, 0, 1, 4)
        connection_device_layout.addLayout(connection_row)

        device_grid = QGridLayout()
        device_grid.setHorizontalSpacing(8)
        device_grid.setVerticalSpacing(3)
        device_grid.addWidget(QLabel("Model"), 0, 0)
        self.device_model_label = QLabel("--")
        self.device_model_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.device_model_label.setWordWrap(True)
        device_grid.addWidget(self.device_model_label, 0, 1)
        device_grid.addWidget(QLabel("Port"), 1, 0)
        self.device_port_label = QLabel("--")
        self.device_port_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.device_port_label.setWordWrap(True)
        device_grid.addWidget(self.device_port_label, 1, 1)
        device_grid.addWidget(QLabel("Manufacturer"), 2, 0)
        self.device_manufacturer_label = QLabel("--")
        self.device_manufacturer_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.device_manufacturer_label.setWordWrap(True)
        device_grid.addWidget(self.device_manufacturer_label, 2, 1)
        device_grid.addWidget(QLabel("Firmware"), 3, 0)
        self.device_firmware_label = QLabel("--")
        self.device_firmware_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.device_firmware_label.setWordWrap(True)
        device_grid.addWidget(self.device_firmware_label, 3, 1)
        device_grid.addWidget(QLabel("Connected at"), 4, 0)
        self.device_connected_at_label = QLabel("--")
        self.device_connected_at_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.device_connected_at_label.setWordWrap(True)
        device_grid.addWidget(self.device_connected_at_label, 4, 1)
        device_grid.addWidget(QLabel("Hardware ID"), 5, 0)
        self.device_hwid_label = QLabel("--")
        self.device_hwid_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.device_hwid_label.setWordWrap(True)
        device_grid.addWidget(self.device_hwid_label, 5, 1)
        connection_device_layout.addLayout(device_grid)

        self.motion_control_form_container = QWidget(self)
        self.motion_control_form_container.hide()
        self.motion_control_form_layout = QVBoxLayout(self.motion_control_form_container)
        self.motion_control_form_layout.setContentsMargins(0, 0, 0, 0)
        self.motion_control_form_layout.setSpacing(0)

        self.motion_control_form_widget = QWidget()
        motion_layout = QGridLayout(self.motion_control_form_widget)
        motion_layout.setContentsMargins(4, 4, 4, 4)
        motion_layout.setHorizontalSpacing(8)
        motion_layout.setVerticalSpacing(4)
        motion_layout.addWidget(QLabel("Scan speed (microseconds)"), 0, 0)
        self.scan_speed_spin = QSpinBox()
        self.scan_speed_spin.setToolTip("Delay between motion steps during scan. Higher value means slower scan")
        self.scan_speed_spin.setRange(200, 20000)
        self.scan_speed_spin.setSingleStep(50)
        self.scan_speed_spin.setValue(600)
        self.scan_speed_spin.valueChanged.connect(self._update_motion_control_summary)
        motion_layout.addWidget(self.scan_speed_spin, 0, 1)
        motion_layout.addWidget(QLabel("Return speed (microseconds)"), 1, 0)
        self.return_speed_spin = QSpinBox()
        self.return_speed_spin.setToolTip("Delay between motion steps when returning to home position")
        self.return_speed_spin.setRange(100, 20000)
        self.return_speed_spin.setSingleStep(50)
        self.return_speed_spin.setValue(300)
        self.return_speed_spin.valueChanged.connect(self._update_motion_control_summary)
        motion_layout.addWidget(self.return_speed_spin, 1, 1)
        motion_layout.addWidget(QLabel("Signal polarity"), 2, 0)
        self.polarity_combo = QComboBox()
        self.polarity_combo.setToolTip("Choose how the detector signal should be interpreted during normalisation")
        self.polarity_combo.addItems([POLARITY_HIGHER_IS_MORE, POLARITY_LOWER_IS_MORE])
        self.polarity_combo.setCurrentText(POLARITY_LOWER_IS_MORE)
        self.polarity_combo.currentTextChanged.connect(self._on_polarity_changed)
        self.polarity_combo.currentTextChanged.connect(self._update_motion_control_summary)
        motion_layout.addWidget(self.polarity_combo, 2, 1)
        preset_row = QHBoxLayout()
        self.motion_preset_slow_button = QPushButton("Slow preset")
        slow_btn = self.motion_preset_slow_button
        slow_btn.clicked.connect(lambda: self._apply_speed_preset(13333, 4000, "Slow"))
        preset_row.addWidget(slow_btn)
        self.motion_preset_standard_button = QPushButton("Standard preset")
        std_btn = self.motion_preset_standard_button
        std_btn.clicked.connect(lambda: self._apply_speed_preset(8000, 3000, "Standard"))
        preset_row.addWidget(std_btn)
        self.motion_preset_fast_button = QPushButton("Fast preset")
        fast_btn = self.motion_preset_fast_button
        fast_btn.clicked.connect(lambda: self._apply_speed_preset(3000, 1200, "Fast"))
        preset_row.addWidget(fast_btn)
        motion_layout.addLayout(preset_row, 3, 0, 1, 2)
        action_row = QHBoxLayout()
        self.motion_read_speeds_button = QPushButton("Read speeds")
        query_speed_button = self.motion_read_speeds_button
        query_speed_button.clicked.connect(self._request_speed_settings)
        action_row.addWidget(query_speed_button)
        self.motion_apply_speeds_button = QPushButton("Apply speeds")
        apply_speed_button = self.motion_apply_speeds_button
        apply_speed_button.clicked.connect(self._apply_speed_settings)
        action_row.addWidget(apply_speed_button)
        self.motion_default_speeds_button = QPushButton("Default speeds")
        default_speed_button = self.motion_default_speeds_button
        default_speed_button.clicked.connect(lambda: self._apply_speed_preset(8000, 3000, "Default"))
        action_row.addWidget(default_speed_button)
        motion_layout.addLayout(action_row, 4, 0, 1, 2)
        self.motion_control_form_layout.addWidget(self.motion_control_form_widget)
        self.motion_control_form_widget.setVisible(False)

        controls_group = QGroupBox("Controls")
        controls_group.setStyleSheet(WINDOW_GROUPBOX_STYLE)
        controls_layout = QGridLayout(controls_group)
        controls_layout.setContentsMargins(6, 4, 6, 4)
        controls_layout.setHorizontalSpacing(4)
        controls_layout.setVerticalSpacing(3)

        def _make_section_title(text_value):
            label = QLabel(text_value)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            label.setStyleSheet("font-size: 11px; font-weight: 600; color: #555555;")
            return label

        scanning_frame = self._make_panel_frame()
        scanning_frame.setStyleSheet(WINDOW_FRAME_STYLE)
        scanning_layout = QGridLayout(scanning_frame)
        scanning_layout.setContentsMargins(6, 6, 6, 6)
        scanning_layout.setHorizontalSpacing(5)
        scanning_layout.setVerticalSpacing(2)
        scanning_layout.addWidget(_make_section_title("Scanning control"), 0, 0, 1, 3)

        start_btn = QPushButton("Start Scan")
        start_btn.setMinimumHeight(22)
        start_btn.setStyleSheet(BUTTON_ACTIVE_STYLE)
        start_btn.clicked.connect(self._start_scan_sequence)
        self.control_buttons["START"] = start_btn
        scanning_layout.addWidget(start_btn, 1, 0)

        stop_btn = QPushButton("Stop Scan")
        stop_btn.setMinimumHeight(22)
        stop_btn.setStyleSheet(BUTTON_ACTIVE_STYLE)
        stop_btn.clicked.connect(lambda checked=False, c="STOP": self._send_command(c))
        self.control_buttons["STOP"] = stop_btn
        scanning_layout.addWidget(stop_btn, 1, 2)

        count_holder = QWidget()
        count_layout = QHBoxLayout(count_holder)
        count_layout.setContentsMargins(0, 0, 0, 0)
        count_layout.setSpacing(4)
        scans_label = QLabel("scans:")
        scans_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        scans_label.setStyleSheet("font-size: 11px; font-weight: 600; color: #555555;")
        count_layout.addWidget(scans_label)
        self.measurement_count_combo = QComboBox()
        self.measurement_count_combo.setToolTip("Choose how many scans should run automatically in sequence, up to 8")
        self.measurement_count_combo.addItems([str(i) for i in range(1, 9)])
        self.measurement_count_combo.setCurrentText("1")
        self.measurement_count_combo.setMinimumWidth(68)
        self.measurement_count_combo.setMaximumWidth(76)
        count_layout.addWidget(self.measurement_count_combo)
        scanning_layout.addWidget(count_holder, 1, 1, alignment=Qt.AlignCenter)

        positioning_frame = self._make_panel_frame()
        positioning_frame.setStyleSheet(WINDOW_FRAME_STYLE)
        positioning_layout = QGridLayout(positioning_frame)
        positioning_layout.setContentsMargins(6, 6, 6, 6)
        positioning_layout.setHorizontalSpacing(4)
        positioning_layout.setVerticalSpacing(2)
        positioning_layout.addWidget(_make_section_title("Positioning and Laser"), 0, 0, 1, 4)

        home_btn = QPushButton("Home position")
        home_btn.setMinimumHeight(18)
        home_btn.setStyleSheet(BUTTON_NEUTRAL_STYLE + " padding: 0 8px;")
        home_btn.clicked.connect(lambda checked=False, c="HOME": self._send_command(c))
        self.control_buttons["HOME"] = home_btn
        positioning_layout.addWidget(home_btn, 1, 0)

        end_btn = QPushButton("End position")
        end_btn.setMinimumHeight(18)
        end_btn.setStyleSheet(BUTTON_NEUTRAL_STYLE + " padding: 0 8px;")
        end_btn.setToolTip("Rotate the arm to the far end position. Requires firmware support")
        end_btn.clicked.connect(lambda checked=False: self._send_command("GO END"))
        self.control_buttons["GOEND"] = end_btn
        positioning_layout.addWidget(end_btn, 1, 1)

        self.laser_toggle_button = QPushButton("Laser On")
        self.laser_toggle_button.setMinimumHeight(18)
        self.laser_toggle_button.setStyleSheet(BUTTON_NEUTRAL_STYLE + " padding: 0 8px;")
        self.laser_toggle_button.setToolTip("Turn the laser on or off while in standby")
        self.laser_toggle_button.clicked.connect(self._toggle_laser_manual)
        self.control_buttons["LASERON"] = self.laser_toggle_button
        positioning_layout.addWidget(self.laser_toggle_button, 1, 2)

        status_btn = QPushButton("Status")
        status_btn.setMinimumHeight(18)
        status_btn.setStyleSheet(BUTTON_NEUTRAL_STYLE + " padding: 0 8px;")
        status_btn.clicked.connect(lambda checked=False, c="STATUS": self._send_command(c))
        self.control_buttons["STATUS"] = status_btn
        positioning_layout.addWidget(status_btn, 1, 3)

        motion_compact_frame = self._make_panel_frame()
        motion_compact_frame.setStyleSheet(WINDOW_FRAME_STYLE)
        motion_compact_layout = QGridLayout(motion_compact_frame)
        motion_compact_layout.setContentsMargins(6, 6, 6, 6)
        motion_compact_layout.setHorizontalSpacing(4)
        motion_compact_layout.setVerticalSpacing(2)
        motion_compact_layout.addWidget(_make_section_title("Motion control"), 0, 0, 1, 2)
        self.motion_control_summary_label = QLabel("<b>Scan:</b> --    <b>Return:</b> --<br><b>Polarity:</b> --")
        self.motion_control_summary_label.setWordWrap(True)
        self.motion_control_summary_label.setStyleSheet("font-size: 10px; line-height: 1.2; color: #333333;")
        self.motion_control_summary_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        motion_compact_layout.addWidget(self.motion_control_summary_label, 1, 0)
        self.motion_control_button = QPushButton("Edit control")
        self.motion_control_button.setMinimumHeight(22)
        self.motion_control_button.setMinimumWidth(104)
        self.motion_control_button.setMaximumWidth(180)
        self.motion_control_button.setStyleSheet("font-weight: 600; padding: 1px 10px;")
        self.motion_control_button.clicked.connect(self._show_motion_control_dialog)
        motion_compact_layout.addWidget(self.motion_control_button, 1, 1, Qt.AlignTop | Qt.AlignRight)

        controls_layout.addWidget(scanning_frame, 1, 0)
        controls_layout.addWidget(positioning_frame, 2, 0)
        controls_layout.addWidget(motion_compact_frame, 3, 0)

        session_actions_frame = self._make_panel_frame()
        session_actions_frame.setStyleSheet(WINDOW_FRAME_STYLE)
        session_actions_layout = QHBoxLayout(session_actions_frame)
        session_actions_layout.setContentsMargins(6, 6, 6, 6)
        session_actions_layout.setSpacing(6)
        session_actions_title = _make_section_title("Session actions")
        session_actions_layout.addWidget(session_actions_title, 0)
        session_actions_layout.addStretch(1)
        self.clear_plot_button = QPushButton("Clear Plot")
        self.clear_plot_button.setMinimumHeight(20)
        self.clear_plot_button.setStyleSheet("background-color: #f3f4f6; border: 1px solid #c4cad2; color: #374151; font-weight: 600; padding: 1px 10px;")
        self.clear_plot_button.clicked.connect(self._clear_measurement)
        session_actions_layout.addWidget(self.clear_plot_button)
        self.clear_session_button = QPushButton("Clear Session")
        self.clear_session_button.setMinimumHeight(20)
        self.clear_session_button.setStyleSheet("background-color: #f3f4f6; border: 1px solid #c4cad2; color: #374151; font-weight: 600; padding: 1px 10px;")
        self.clear_session_button.clicked.connect(self._clear_session)
        session_actions_layout.addWidget(self.clear_session_button)
        controls_layout.addWidget(session_actions_frame, 4, 0)

        self.controls_status_label = QLabel("")
        self.controls_status_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.controls_status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.controls_status_label.setStyleSheet("font-size: 10px; color: #555555; padding-top: 1px;")
        controls_layout.addWidget(self.controls_status_label, 5, 0)
        measurement_setup_group = QGroupBox("Measurement Setup")
        measurement_setup_group.setStyleSheet(WINDOW_GROUPBOX_STYLE)
        measurement_setup_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        measurement_setup_group_layout = QVBoxLayout(measurement_setup_group)
        measurement_setup_group_layout.setContentsMargins(8, 8, 8, 8)
        measurement_setup_group_layout.setSpacing(8)

        summary_row = QHBoxLayout()
        summary_row.setContentsMargins(0, 0, 0, 0)
        summary_row.setSpacing(10)
        self.measurement_setup_summary_label = QLabel("<table cellspacing='2' cellpadding='3' style='font-size:11px; color:#333333;'><tr><td style='padding-right:28px; padding-bottom:2px;'><b>Diode Model:</b> --</td><td style='padding-bottom:2px;'><b>Bench Config:</b> --</td></tr><tr><td style='padding-right:28px; padding-bottom:2px;'><b>Diode Type:</b> --</td><td style='padding-bottom:2px;'><b>Test ID:</b> --</td></tr><tr><td style='padding-right:28px;'><b>Diffuser Used:</b> --</td><td><b>Operator:</b> --</td></tr></table>")
        self.measurement_setup_summary_label.setWordWrap(True)
        self.measurement_setup_summary_label.setStyleSheet("font-size: 11px; line-height: 1.35; color: #333333;")
        self.measurement_setup_summary_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        summary_row.addWidget(self.measurement_setup_summary_label, 1)
        self.measurement_setup_button = QPushButton("Edit setup")
        self.measurement_setup_button.setMinimumHeight(22)
        self.measurement_setup_button.setMinimumWidth(104)
        self.measurement_setup_button.setStyleSheet("font-weight: 600; padding: 1px 8px;")
        self.measurement_setup_button.clicked.connect(self._show_measurement_setup_dialog)
        summary_row.addWidget(self.measurement_setup_button, 0, Qt.AlignTop)
        measurement_setup_group_layout.addLayout(summary_row)

        self.measurement_setup_form_layout = QVBoxLayout()
        self.measurement_setup_form_layout.setContentsMargins(0, 0, 0, 0)
        self.measurement_setup_form_layout.setSpacing(0)
        measurement_setup_group_layout.addLayout(self.measurement_setup_form_layout)

        self.measurement_setup_form_widget = QWidget()
        measurement_setup_layout = QGridLayout(self.measurement_setup_form_widget)
        measurement_setup_layout.setContentsMargins(4, 4, 4, 4)
        measurement_setup_layout.setHorizontalSpacing(8)
        measurement_setup_layout.setVerticalSpacing(4)
        measurement_setup_layout.addWidget(QLabel("Diode model"), 0, 0)
        measurement_setup_layout.addWidget(self.diode_model_edit, 0, 1)
        measurement_setup_layout.addWidget(QLabel("Operator"), 0, 2)
        self.operator_edit.textChanged.connect(self._on_metadata_changed)
        measurement_setup_layout.addWidget(self.operator_edit, 0, 3)
        measurement_setup_layout.addWidget(QLabel("Diode type"), 1, 0)
        self.diode_type_edit.textChanged.connect(self._on_metadata_changed)
        measurement_setup_layout.addWidget(self.diode_type_edit, 1, 1)
        measurement_setup_layout.addWidget(QLabel("Diffuser used"), 1, 2)
        self.diffuser_edit.textChanged.connect(self._on_metadata_changed)
        measurement_setup_layout.addWidget(self.diffuser_edit, 1, 3)
        measurement_setup_layout.addWidget(QLabel("Bench config"), 2, 0)
        self.bench_config_edit.textChanged.connect(self._on_metadata_changed)
        measurement_setup_layout.addWidget(self.bench_config_edit, 2, 1)
        measurement_setup_layout.addWidget(QLabel("Test ID"), 2, 2)
        self.test_id_edit.textChanged.connect(self._on_metadata_changed)
        measurement_setup_layout.addWidget(self.test_id_edit, 2, 3)
        measurement_setup_layout.addWidget(QLabel("Export filename"), 3, 0)
        measurement_setup_layout.addWidget(self.export_preview_label, 3, 1)
        measurement_setup_layout.addWidget(QLabel("Measurement notes"), 4, 0)
        measurement_setup_layout.addWidget(self.notes_edit, 4, 1, 1, 3)
        measurement_setup_layout.addWidget(QLabel("Output folder"), 5, 0)
        folder_row = QHBoxLayout()
        folder_row.addWidget(self.output_folder_edit)
        self.browse_output_folder_button = QPushButton("Browse")
        browse_button = self.browse_output_folder_button
        browse_button.setMinimumHeight(24)
        browse_button.clicked.connect(self._browse_output_folder)
        folder_row.addWidget(browse_button)
        measurement_setup_layout.addLayout(folder_row, 5, 1, 1, 3)
        self.measurement_setup_form_layout.addWidget(self.measurement_setup_form_widget)
        self.measurement_setup_form_widget.setVisible(False)
        content_splitter = QSplitter(Qt.Horizontal)
        self.content_splitter = content_splitter
        content_splitter.setHandleWidth(6)
        main_layout.addWidget(content_splitter, 1)

        graphs_panel = self._make_panel_frame()
        graphs_layout = QHBoxLayout(graphs_panel)
        graphs_layout.setContentsMargins(4, 4, 4, 4)
        graph_splitter = QSplitter(Qt.Horizontal)
        self.graph_column_splitter = graph_splitter
        graph_splitter.setHandleWidth(4)
        graphs_layout.addWidget(graph_splitter)

        if FigureCanvas is None or Figure is None:
            placeholder = QLabel("matplotlib Qt backend is not available. Install matplotlib to show the graphs.")
            placeholder.setWordWrap(True)
            placeholder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            graph_splitter.addWidget(placeholder)
        else:
            left_plot_column = QWidget()
            left_plot_layout = QVBoxLayout(left_plot_column)
            left_plot_layout.setContentsMargins(0, 0, 0, 0)
            left_plot_layout.setSpacing(2)

            self.main_plot_splitter = QSplitter(Qt.Vertical)
            self.main_plot_splitter.setChildrenCollapsible(True)
            self.main_plot_splitter.setHandleWidth(6)

            top_plot_panel = QWidget()
            top_plot_layout = QHBoxLayout(top_plot_panel)
            top_plot_layout.setContentsMargins(0, 0, 0, 0)
            top_plot_layout.setSpacing(2)

            self.figure = Figure(figsize=(9.6, 5.2), dpi=100)
            self.ax = self.figure.add_subplot(111)
            self.canvas = FigureCanvas(self.figure)
            top_plot_layout.addWidget(self.canvas, 1)

            graph1_side_panel = QWidget()
            graph1_side_panel.setMinimumWidth(165)
            graph1_side_panel.setMaximumWidth(165)
            graph1_side_layout = QVBoxLayout(graph1_side_panel)
            graph1_side_layout.setContentsMargins(0, 0, 8, 2)
            graph1_side_layout.setSpacing(4)

            graph1_settings_frame = self._make_panel_frame()
            graph1_settings_layout = QVBoxLayout(graph1_settings_frame)
            graph1_settings_layout.setContentsMargins(8, 8, 8, 8)
            graph1_settings_layout.setSpacing(4)
            graph1_settings_label = QLabel("Graph settings")
            graph1_settings_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            graph1_settings_label.setStyleSheet("font-size: 11px; font-weight: 600;")
            graph1_settings_layout.addWidget(graph1_settings_label)
            self.g1_ideal_check = QCheckBox("Ideal cosine")
            self.g1_ideal_check.setToolTip("Show or hide the ideal cosine reference curve on Graph 1: Cosine Response")
            self.g1_ideal_check.setChecked(True)
            self.g1_ideal_check.toggled.connect(self._sync_graph_options_from_controls)
            graph1_settings_layout.addWidget(self.g1_ideal_check)
            self.g1_current_check = QCheckBox(self.current_scan_label)
            self.g1_current_check.setToolTip("Show or hide the current scan on Graph 1: Cosine Response")
            self.g1_current_check.setChecked(True)
            self.g1_current_check.toggled.connect(self._sync_graph_options_from_controls)
            graph1_settings_layout.addWidget(self.g1_current_check)
            self.g1_mirror_check = QCheckBox("Mirrored Curve")
            self.g1_mirror_check.setToolTip("Overlay the mirrored version of the current scan to assess symmetry")
            self.g1_mirror_check.setChecked(False)
            self.g1_mirror_check.toggled.connect(self._sync_graph_options_from_controls)
            graph1_settings_layout.addWidget(self.g1_mirror_check)
            self.g1_grid_check = QCheckBox("Grid")
            self.g1_grid_check.setChecked(True)
            self.g1_grid_check.toggled.connect(self._sync_graph_options_from_controls)
            graph1_settings_layout.addWidget(self.g1_grid_check)
            self.g1_error_band_check = QCheckBox("Show Error Band")
            self.g1_error_band_check.setToolTip("Highlight the difference between the measured response and the ideal cosine on Graph 1: Cosine Response")
            self.g1_error_band_check.setChecked(False)
            self.g1_error_band_check.toggled.connect(self._sync_graph_options_from_controls)
            graph1_settings_layout.addWidget(self.g1_error_band_check)
            graph1_mode_label = QLabel("Normalise mode")
            graph1_mode_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            graph1_mode_label.setStyleSheet("font-size: 10px; color: #555555;")
            graph1_settings_layout.addWidget(graph1_mode_label)
            self.g1_mode_combo = QComboBox()
            self.g1_mode_combo.setToolTip("Switch Graph 1: Cosine Response between normalised response and raw detector voltage")
            self.g1_mode_combo.addItems(["Normalised", "Raw voltage"])
            self.g1_mode_combo.currentTextChanged.connect(self._sync_graph_options_from_controls)
            graph1_settings_layout.addWidget(self.g1_mode_combo)
            graph1_side_layout.addWidget(graph1_settings_frame, 0)
            graph1_side_layout.addStretch(1)
            self.graph1_export_toggle_button = QPushButton("Export")
            self.graph1_export_toggle_button.setMinimumHeight(24)
            self.graph1_export_toggle_button.setMinimumWidth(80)
            self.graph1_export_toggle_button.setMaximumWidth(80)
            self.graph1_export_toggle_button.setStyleSheet("font-weight: 600;")
            self.graph1_export_toggle_button.clicked.connect(lambda: self._show_export_popup("graph1", self.graph1_export_toggle_button))
            graph1_side_layout.addWidget(self.graph1_export_toggle_button, 0, Qt.AlignRight | Qt.AlignBottom)


            self.graph1_export_frame = self._make_panel_frame()
            self.graph1_export_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
            graph1_export_layout = QVBoxLayout(self.graph1_export_frame)
            graph1_export_layout.setContentsMargins(8, 8, 8, 8)
            graph1_export_layout.setSpacing(4)
            graph1_export_label = QLabel("Export")
            graph1_export_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            graph1_export_label.setStyleSheet("font-size: 11px; font-weight: 600;")
            graph1_export_layout.addWidget(graph1_export_label)

            self.graph1_export_png_check = QCheckBox("Graph (png)")
            self.graph1_export_png_check.setChecked(True)
            graph1_export_layout.addWidget(self.graph1_export_png_check)
            self.graph1_export_csv_check = QCheckBox("Scan Data (csv)")
            self.graph1_export_csv_check.setChecked(False)
            graph1_export_layout.addWidget(self.graph1_export_csv_check)
            self.graph1_export_button = QPushButton("Export scan")
            self.graph1_export_button.setToolTip("Export the current Graph 1: Cosine Response view using the selected export options")
            self.graph1_export_button.setMinimumHeight(24)
            self.graph1_export_button.clicked.connect(self._export_graph1_selected)
            graph1_export_layout.addWidget(self.graph1_export_button)
            self.graph1_export_frame.hide()
            self._set_export_panel_visibility("graph1", False)

            top_plot_layout.addWidget(graph1_side_panel)
            self.main_plot_splitter.addWidget(top_plot_panel)

            bottom_plot_panel = QWidget()
            bottom_plot_layout = QHBoxLayout(bottom_plot_panel)
            bottom_plot_layout.setContentsMargins(0, 0, 0, 0)
            bottom_plot_layout.setSpacing(2)

            self.compare_figure = Figure(figsize=(9.6, 2.2), dpi=100)
            self.compare_ax = self.compare_figure.add_subplot(111)
            self.compare_canvas = FigureCanvas(self.compare_figure)
            bottom_plot_layout.addWidget(self.compare_canvas, 1)

            compare_side_panel = QWidget()
            compare_side_panel.setMinimumWidth(165)
            compare_side_panel.setMaximumWidth(165)
            compare_side_layout = QVBoxLayout(compare_side_panel)
            compare_side_layout.setContentsMargins(0, 0, 8, 2)
            compare_side_layout.setSpacing(4)

            graph2_settings_frame = self._make_panel_frame()
            graph2_settings_layout = QVBoxLayout(graph2_settings_frame)
            graph2_settings_layout.setContentsMargins(8, 8, 8, 8)
            graph2_settings_layout.setSpacing(4)
            graph2_settings_label = QLabel("Graph settings")
            graph2_settings_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            graph2_settings_label.setStyleSheet("font-size: 11px; font-weight: 600;")
            graph2_settings_layout.addWidget(graph2_settings_label)
            self.g2_ideal_check = QCheckBox("Ideal cosine")
            self.g2_ideal_check.setToolTip("Show or hide the ideal cosine reference curve on Graph 2: Cosine Response Comparison")
            self.g2_ideal_check.setChecked(True)
            self.g2_ideal_check.toggled.connect(self._sync_graph_options_from_controls)
            graph2_settings_layout.addWidget(self.g2_ideal_check)
            self.g2_grid_check = QCheckBox("Grid")
            self.g2_grid_check.setChecked(True)
            self.g2_grid_check.toggled.connect(self._sync_graph_options_from_controls)
            graph2_settings_layout.addWidget(self.g2_grid_check)
            self.g2_error_band_check = QCheckBox("Show Error Band")
            self.g2_error_band_check.setToolTip("Highlight the difference between displayed scans and the ideal cosine on Graph 2: Cosine Response Comparison")
            self.g2_error_band_check.setChecked(False)
            self.g2_error_band_check.toggled.connect(self._sync_graph_options_from_controls)
            graph2_settings_layout.addWidget(self.g2_error_band_check)
            graph2_mode_label = QLabel("Normalise mode")
            graph2_mode_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            graph2_mode_label.setStyleSheet("font-size: 10px; color: #555555;")
            graph2_settings_layout.addWidget(graph2_mode_label)
            self.g2_mode_combo = QComboBox()
            self.g2_mode_combo.setToolTip("Switch Graph 2: Cosine Response Comparison between normalised response and raw detector voltage")
            self.g2_mode_combo.addItems(["Normalised", "Raw voltage"])
            self.g2_mode_combo.currentTextChanged.connect(self._sync_graph_options_from_controls)
            graph2_settings_layout.addWidget(self.g2_mode_combo)
            graph2_settings_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
            compare_side_layout.addWidget(graph2_settings_frame, 0)

            scan_manager_frame = self._make_panel_frame()
            scan_manager_frame.setMinimumHeight(120)
            scan_manager_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            scan_manager_layout = QVBoxLayout(scan_manager_frame)
            scan_manager_layout.setContentsMargins(0, 0, 0, 0)
            scan_manager_layout.setSpacing(4)
            self.compare_panel_title_label = QLabel("Scans")
            self.compare_panel_title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.compare_panel_title_label.setStyleSheet("font-size: 11px; font-weight: 600;")
            scan_manager_layout.addWidget(self.compare_panel_title_label)

            self.compare_scan_list_widget = QListWidget()
            self.compare_scan_list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.compare_scan_list_widget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
            self.compare_scan_list_widget.setMinimumWidth(0)
            self.compare_scan_list_widget.setMaximumWidth(16777215)
            self.compare_scan_list_widget.setFrameShape(QFrame.NoFrame)
            self.compare_scan_list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.compare_scan_list_widget.setUniformItemSizes(True)
            self.compare_scan_list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.compare_scan_list_widget.setContentsMargins(0, 0, 0, 0)
            self.compare_scan_list_widget.setViewportMargins(0, 0, 0, 0)
            self.compare_scan_list_widget.setStyleSheet("""
                QListWidget {
                    padding: 0px;
                    margin: 0px;
                    border: none;
                }
                QScrollBar:vertical {
                    width: 10px;
                    margin: 0px;
                    padding: 0px;
                }
                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)
            self.compare_scan_list_widget.itemChanged.connect(self._on_scan_visibility_changed)
            self.compare_scan_list_widget.itemDoubleClicked.connect(self._rename_scan_from_item)
            self.compare_scan_list_widget.itemSelectionChanged.connect(self._update_scan_manager_buttons)
            scan_manager_layout.addWidget(self.compare_scan_list_widget, 1)

            compare_button_row_1 = QHBoxLayout()
            compare_button_row_1.setSpacing(4)
            self.rename_scan_button = QPushButton("Edit")
            self.rename_scan_button.setToolTip("Rename the selected scan and change its colour")
            self.rename_scan_button.setMinimumHeight(24)
            self.rename_scan_button.clicked.connect(self._rename_selected_scan)
            compare_button_row_1.addWidget(self.rename_scan_button)
            self.delete_scan_button = QPushButton("Delete")
            self.delete_scan_button.setToolTip("Delete the selected stored scan from Graph 2: Cosine Response Comparison")
            self.delete_scan_button.setMinimumHeight(24)
            self.delete_scan_button.clicked.connect(self._delete_selected_scan)
            compare_button_row_1.addWidget(self.delete_scan_button)
            scan_manager_layout.addLayout(compare_button_row_1)

            compare_button_row_2 = QHBoxLayout()
            compare_button_row_2.setSpacing(4)
            self.clear_scans_button = QPushButton("Clear")
            self.clear_scans_button.setToolTip("Clear all stored scans from the Graph 2: Cosine Response Comparison scan list")
            self.clear_scans_button.setMinimumHeight(24)
            self.clear_scans_button.clicked.connect(self._clear_stored_scans)
            compare_button_row_2.addWidget(self.clear_scans_button)
            scan_manager_layout.addLayout(compare_button_row_2)
            compare_side_layout.addWidget(scan_manager_frame, 1)
            compare_side_layout.addSpacing(2)
            self.graph2_export_toggle_button = QPushButton("Export")
            self.graph2_export_toggle_button.setMinimumHeight(24)
            self.graph2_export_toggle_button.setMinimumWidth(80)
            self.graph2_export_toggle_button.setMaximumWidth(80)
            self.graph2_export_toggle_button.setStyleSheet("font-weight: 600;")
            self.graph2_export_toggle_button.clicked.connect(lambda: self._show_export_popup("graph2", self.graph2_export_toggle_button))


            self.graph2_export_frame = self._make_panel_frame()
            compare_export_layout = QVBoxLayout(self.graph2_export_frame)
            compare_export_layout.setContentsMargins(8, 8, 8, 8)
            compare_export_layout.setSpacing(4)
            compare_export_label = QLabel("Export")
            compare_export_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            compare_export_label.setStyleSheet("font-size: 11px; font-weight: 600;")
            compare_export_layout.addWidget(compare_export_label)
            self.graph2_export_png_check = QCheckBox("Graph (png)")
            self.graph2_export_png_check.setChecked(True)
            compare_export_layout.addWidget(self.graph2_export_png_check)
            self.graph2_export_csv_check = QCheckBox("Scan Data (csv)*")
            self.graph2_export_csv_check.setChecked(False)
            compare_export_layout.addWidget(self.graph2_export_csv_check)
            self.graph2_export_avg_csv_check = QCheckBox("Average Scan Data (csv)")
            self.graph2_export_avg_csv_check.setChecked(False)
            compare_export_layout.addWidget(self.graph2_export_avg_csv_check)
            self.graph2_export_note_label = QLabel("*all displayed data")
            self.graph2_export_note_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.graph2_export_note_label.setStyleSheet("font-size: 9px; color: #666666;")
            compare_export_layout.addWidget(self.graph2_export_note_label)
            self.graph2_export_button = QPushButton("Export scan")
            self.graph2_export_button.setToolTip("Export the current Graph 2: Cosine Response Comparison view using only the scans that are currently displayed")
            self.graph2_export_button.setMinimumHeight(24)
            self.graph2_export_button.clicked.connect(self._export_graph2_selected)
            compare_export_layout.addWidget(self.graph2_export_button)
            self.graph2_export_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
            compare_side_layout.addWidget(self.graph2_export_toggle_button, 0, Qt.AlignRight | Qt.AlignBottom)
            self.graph2_export_frame.hide()
            self._set_export_panel_visibility("graph2", False)

            bottom_plot_layout.addWidget(compare_side_panel)
            self.main_plot_splitter.addWidget(bottom_plot_panel)

            error_plot_panel = QWidget()
            error_plot_layout = QHBoxLayout(error_plot_panel)
            error_plot_layout.setContentsMargins(0, 0, 0, 0)
            error_plot_layout.setSpacing(2)

            self.error_figure = Figure(figsize=(9.6, 2.0), dpi=100)
            self.error_ax = self.error_figure.add_subplot(111)
            self.error_canvas = FigureCanvas(self.error_figure)
            error_plot_layout.addWidget(self.error_canvas, 1)

            self.error_side_panel = QWidget()
            self.error_side_panel.setMinimumWidth(165)
            self.error_side_panel.setMaximumWidth(165)
            error_side_layout = QVBoxLayout(self.error_side_panel)
            error_side_layout.setContentsMargins(0, 0, 8, 2)
            error_side_layout.setSpacing(4)
            self.error_status_label = QLabel("")
            self.error_status_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.error_status_label.setWordWrap(True)
            self.error_status_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.error_status_label.setVisible(False)
            self.error_status_label.setStyleSheet("font-size: 10px; color: #555555;")
            error_side_layout.addWidget(self.error_status_label)
            self.error_export_toggle_button = QPushButton("Export")
            self.error_export_toggle_button.setMinimumHeight(24)
            self.error_export_toggle_button.setMinimumWidth(80)
            self.error_export_toggle_button.setMaximumWidth(80)
            self.error_export_toggle_button.setStyleSheet("font-weight: 600;")
            self.error_export_toggle_button.clicked.connect(lambda: self._show_export_popup("error", self.error_export_toggle_button))
            error_side_layout.addStretch(1)
            error_side_layout.addSpacing(2)
            error_side_layout.addWidget(self.error_export_toggle_button, 0, Qt.AlignRight | Qt.AlignBottom)

            self.error_export_frame = self._make_panel_frame()
            self.error_export_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
            error_export_layout = QVBoxLayout(self.error_export_frame)
            error_export_layout.setContentsMargins(8, 8, 8, 8)
            error_export_layout.setSpacing(4)
            error_export_label = QLabel("Export")
            error_export_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            error_export_label.setStyleSheet("font-size: 11px; font-weight: 600;")
            error_export_layout.addWidget(error_export_label)
            self.error_export_png_check = QCheckBox("Graph (png)")
            self.error_export_png_check.setChecked(True)
            error_export_layout.addWidget(self.error_export_png_check)
            self.error_export_csv_check = QCheckBox("Scan Data (csv)")
            self.error_export_csv_check.setChecked(False)
            error_export_layout.addWidget(self.error_export_csv_check)
            self.error_export_button = QPushButton("Export scan")
            self.error_export_button.setToolTip("Export the current Cosine Error graph or its data")
            self.error_export_button.setMinimumHeight(24)
            self.error_export_button.clicked.connect(self._export_error_selected)
            error_export_layout.addWidget(self.error_export_button)
            self.error_export_frame.hide()
            self._set_export_panel_visibility("error", False)
            error_plot_layout.addWidget(self.error_side_panel)

            self.main_plot_splitter.addWidget(error_plot_panel)
            self.main_plot_splitter.setSizes([400, 500, 170])

            left_plot_layout.addWidget(self.main_plot_splitter, 1)

            graph_splitter.addWidget(left_plot_column)

            right_graph_column = QWidget()
            right_graph_layout = QVBoxLayout(right_graph_column)
            right_graph_layout.setContentsMargins(0, 0, 0, 0)
            right_graph_layout.setSpacing(6)

            status_panel = self._make_panel_frame()
            status_panel.setStyleSheet(WINDOW_FRAME_STYLE)
            status_outer = QVBoxLayout(status_panel)
            status_outer.setContentsMargins(10, 10, 10, 10)
            status_outer.setSpacing(8)

            status_outer.addWidget(connection_device_group)
            status_outer.addWidget(measurement_setup_group)
            status_outer.addWidget(controls_group)

            measurement_group = QGroupBox("Measurement")
            measurement_group.setStyleSheet(WINDOW_GROUPBOX_STYLE)
            measurement_outer = QVBoxLayout(measurement_group)
            measurement_outer.setContentsMargins(8, 8, 8, 8)
            measurement_outer.setSpacing(5)

            measurement_header = QHBoxLayout()
            measurement_header.setContentsMargins(0, 0, 0, 0)
            measurement_header.setSpacing(6)
            self.mode_label = QLabel("Mode: IDLE")
            self.mode_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.mode_label.setWordWrap(True)
            self.mode_label.setStyleSheet("font-weight: 700; font-size: 13px; color: #111111;")
            self.mode_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            controls_layout.addWidget(self.mode_label, 0, 0, Qt.AlignLeft | Qt.AlignTop)
            self.samples_label = QLabel("Status: Ready")
            self.samples_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.samples_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.samples_label.setWordWrap(False)
            self.samples_label.setStyleSheet("font-weight: 700; font-size: 13px; color: #111111;")
            self.samples_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
            self.samples_label.setMinimumWidth(180)

            measurement_header.addWidget(self.samples_label, 0, Qt.AlignLeft | Qt.AlignVCenter)
            measurement_header.addStretch(1)
            measurement_outer.addLayout(measurement_header)

            progress_row = QHBoxLayout()
            progress_row.setContentsMargins(0, 0, 0, 0)
            progress_row.setSpacing(6)
            self.progress_bar = QProgressBar()
            self.progress_bar.setRange(0, MAX_POINTS)
            self.progress_bar.setValue(0)
            self.progress_bar.setTextVisible(False)
            self.progress_bar.setMinimumHeight(9)
            self.progress_bar.setMaximumHeight(9)
            self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #bfc7cf;
                    border-radius: 4px;
                    background: #f4f6f8;
                }
                QProgressBar::chunk {
                    border-radius: 4px;
                    background-color: #2f7ed8;
                }
            """)
            self.progress_value_label = QLabel(f"0/{MAX_POINTS}")
            self.progress_value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.progress_value_label.setStyleSheet("font-weight: 600; font-size: 12px; color: #111111;")
            self.progress_value_label.setMinimumWidth(54)
            progress_row.addWidget(self.progress_bar, 1)
            progress_row.addWidget(self.progress_value_label, 0)
            measurement_outer.addLayout(progress_row)

            environment_layout = QHBoxLayout()
            environment_layout.setContentsMargins(0, 2, 0, 0)
            environment_layout.setSpacing(10)

            temp_block = QVBoxLayout()
            temp_block.setContentsMargins(0, 0, 0, 0)
            temp_block.setSpacing(1)
            self.temp_label = QLabel("Temperature: --")
            self.temp_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.temp_label.setWordWrap(True)
            self.temp_label.setStyleSheet("font-weight: 600; font-size: 12px; color: #111111;")
            self.temp_gauge = EnvironmentGauge(0, 50, 15, 35, "°C", "#ffb74d")
            self.temp_gauge.setMinimumHeight(34)
            self.temp_gauge.setMaximumHeight(38)
            temp_block.addWidget(self.temp_label, 0, Qt.AlignLeft | Qt.AlignBottom)
            temp_block.addWidget(self.temp_gauge, 0, Qt.AlignTop)
            environment_layout.addLayout(temp_block, 1)

            humidity_block = QVBoxLayout()
            humidity_block.setContentsMargins(0, 0, 0, 0)
            humidity_block.setSpacing(1)
            self.humidity_label = QLabel("Humidity: --")
            self.humidity_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.humidity_label.setWordWrap(True)
            self.humidity_label.setStyleSheet("font-weight: 600; font-size: 12px; color: #111111;")
            self.humidity_gauge = EnvironmentGauge(0, 100, 20, 60, "%", "#64b5f6")
            self.humidity_gauge.setMinimumHeight(34)
            self.humidity_gauge.setMaximumHeight(38)
            humidity_block.addWidget(self.humidity_label, 0, Qt.AlignLeft | Qt.AlignBottom)
            humidity_block.addWidget(self.humidity_gauge, 0, Qt.AlignTop)
            environment_layout.addLayout(humidity_block, 1)

            measurement_outer.addLayout(environment_layout)

            measurement_divider = QFrame()
            measurement_divider.setFrameShape(QFrame.HLine)
            measurement_divider.setFrameShadow(QFrame.Plain)
            measurement_divider.setStyleSheet("color: #d7d7d7;")
            measurement_outer.addWidget(measurement_divider)

            scan_info_divider = QFrame()
            scan_info_divider.setFrameShape(QFrame.HLine)
            scan_info_divider.setFrameShadow(QFrame.Plain)
            scan_info_divider.setStyleSheet("color: #e0e0e0;")
            measurement_outer.addWidget(scan_info_divider)

            self.scan_info_title_label = QLabel("Scan info")
            self.scan_info_title_label.setStyleSheet("font-size: 11px; font-weight: 600; color: #7a7a7a; padding-top: 3px;")
            measurement_outer.addWidget(self.scan_info_title_label)

            scan_info_grid = QGridLayout()
            scan_info_grid.setContentsMargins(0, 0, 0, 0)
            scan_info_grid.setHorizontalSpacing(18)
            scan_info_grid.setVerticalSpacing(4)
            scan_info_grid.setColumnStretch(0, 1)
            scan_info_grid.setColumnStretch(1, 1)

            self.rmse_label = QLabel("RMSE (≤ 80°): --")
            self.rmse_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.rmse_label.setWordWrap(True)
            self.rmse_label.setStyleSheet("font-size: 12px; color: #111111;")
            scan_info_grid.addWidget(self.rmse_label, 0, 0)

            self.centre_value_label = QLabel("Response at 0° (normalised): --")
            self.centre_value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.centre_value_label.setWordWrap(True)
            self.centre_value_label.setStyleSheet("font-size: 12px; color: #111111;")
            scan_info_grid.addWidget(self.centre_value_label, 0, 1)

            self.symmetry_label = QLabel("Symmetry error (|+θ − −θ| mean): --")
            self.symmetry_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.symmetry_label.setWordWrap(True)
            self.symmetry_label.setStyleSheet("font-size: 12px; color: #111111;")
            scan_info_grid.addWidget(self.symmetry_label, 1, 0)

            self.peak_angle_label = QLabel("Peak offset from 0° (max response): --")
            self.peak_angle_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.peak_angle_label.setWordWrap(True)
            self.peak_angle_label.setStyleSheet("font-size: 12px; color: #111111;")
            scan_info_grid.addWidget(self.peak_angle_label, 1, 1)

            self.scan_finished_label = QLabel("Finished: --")
            self.scan_finished_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.scan_finished_label.setWordWrap(True)
            self.scan_finished_label.setStyleSheet("font-size: 12px; color: #111111;")
            scan_info_grid.addWidget(self.scan_finished_label, 2, 0)

            self.scan_duration_label = QLabel("Duration: --")
            self.scan_duration_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.scan_duration_label.setWordWrap(True)
            self.scan_duration_label.setStyleSheet("font-size: 12px; color: #111111;")
            scan_info_grid.addWidget(self.scan_duration_label, 2, 1)
            measurement_outer.addLayout(scan_info_grid)

            self.scan_summary_label = QLabel("--")
            self.scan_summary_label.setWordWrap(True)
            self.scan_summary_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.scan_summary_label.setStyleSheet("padding-top: 2px; color: #222222; font-size: 12px;")
            measurement_outer.addWidget(self.scan_summary_label)

            self.scan_summary_secondary_label = QLabel("")
            self.scan_summary_secondary_label.setWordWrap(True)
            self.scan_summary_secondary_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.scan_summary_secondary_label.setStyleSheet("color: #222222; font-size: 12px; padding-top: 0px;")
            self.scan_summary_secondary_label.setVisible(False)
            measurement_outer.addWidget(self.scan_summary_secondary_label)

            status_outer.addWidget(measurement_group)

            alignment_group = QGroupBox("Alignment")
            alignment_group.setStyleSheet(WINDOW_GROUPBOX_STYLE)
            alignment_layout = QGridLayout(alignment_group)
            alignment_layout.setHorizontalSpacing(8)
            alignment_layout.setVerticalSpacing(6)
            self.alignment_scale_label = QLabel("Signal Voltage | Best: --")
            self.alignment_scale_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.alignment_scale_label.setStyleSheet("padding-top: 0px; padding-bottom: 0px;")
            self.alignment_bar = AlignmentStrengthBar(0.0, 5000.0)
            self.alignment_bar.setMinimumWidth(280)
            self.alignment_bar.setMaximumWidth(340)
            self.live_hold_combo = QComboBox()
            self.live_hold_combo.setToolTip("Choose whether the live alignment value is shown raw or averaged over recent samples")
            self.live_hold_combo.addItems(["Raw live value", "5 sample average", "10 sample average"])
            self.free_measure_button = QPushButton("Live Measure")
            self.free_measure_button.setMinimumHeight(24)
            self.free_measure_button.setMaximumWidth(110)
            self.free_measure_button.setStyleSheet(BUTTON_ACTIVE_STYLE + " padding: 0 10px;")
            self.free_measure_button.clicked.connect(lambda checked=False, c="FREE": self._send_command(c))
            self.control_buttons["FREE"] = self.free_measure_button
            self.stop_live_button = QPushButton("Stop")
            self.stop_live_button.setMinimumHeight(24)
            self.stop_live_button.setMaximumWidth(110)
            self.stop_live_button.setStyleSheet(BUTTON_DISABLED_STYLE + " padding: 0 10px;")
            self.stop_live_button.setToolTip("Stop the live measurement mode")
            self.stop_live_button.clicked.connect(lambda checked=False, c="STOP": self._send_command(c))
            self.reset_best_button = QPushButton("Reset best")
            self.reset_best_button.setMinimumHeight(24)
            self.reset_best_button.setMaximumWidth(110)
            self.reset_best_button.setStyleSheet(RESET_BEST_BUTTON_STYLE)
            self.reset_best_button.setToolTip("Clear the best alignment marker and start tracking again")
            self.reset_best_button.clicked.connect(self._reset_peak)

            control_row = QHBoxLayout()
            control_row.setContentsMargins(0, 0, 0, 0)
            control_row.setSpacing(10)
            control_row.addWidget(QLabel("Live value mode"), 0)
            control_row.addWidget(self.live_hold_combo, 1)
            control_row.addWidget(self.free_measure_button, 0)
            control_row.addWidget(self.stop_live_button, 0)
            control_row.addWidget(self.reset_best_button, 0)
            self.trend_live_checkbox = QCheckBox("Trend On")
            self.trend_live_checkbox.setChecked(True)
            self.trend_live_checkbox.toggled.connect(lambda _v: self._redraw_alignment_plot())
            control_row.addWidget(self.trend_live_checkbox, 0)
            alignment_layout.addLayout(control_row, 0, 0, 1, 4)

            signal_row = QHBoxLayout()
            signal_row.setContentsMargins(0, 10, 0, 2)
            signal_row.setSpacing(10)
            signal_row.addStretch(1)
            signal_row.addWidget(self.alignment_scale_label, 0, Qt.AlignVCenter)
            signal_row.addWidget(self.alignment_bar, 1)
            signal_row.addStretch(1)
            trend_header = QHBoxLayout()
            trend_header.setContentsMargins(0, 0, 0, 0)
            trend_header.setSpacing(6)
            trend_title = QLabel("Live Alignment Trend")
            trend_title.setAlignment(Qt.AlignCenter)
            trend_title.setStyleSheet("font-size: 14px; font-weight: 600; background: transparent; border: none; padding: 0px; margin: 0px;")
            trend_header.addWidget(self.trend_live_checkbox, 0, Qt.AlignLeft | Qt.AlignVCenter)
            trend_header.addStretch(1)

            alignment_layout.addLayout(signal_row, 1, 0, 1, 4)
            alignment_layout.addLayout(trend_header, 2, 0, 1, 4)
            self.alignment_figure = Figure(figsize=(4.0, 3.0), dpi=100)
            self.alignment_ax = self.alignment_figure.add_subplot(111)
            self.alignment_canvas = FigureCanvas(self.alignment_figure)
            self.alignment_canvas.setMinimumHeight(100)

            alignment_graph_container = QWidget()
            alignment_graph_container.setStyleSheet("background-color: #ffffff; border: 1px solid #d9d9d9;")
            alignment_graph_layout = QVBoxLayout(alignment_graph_container)
            alignment_graph_layout.setContentsMargins(8, 2, 8, 8)
            alignment_graph_layout.setSpacing(1)
            alignment_graph_layout.addWidget(trend_title, 0, Qt.AlignHCenter)
            alignment_graph_layout.addWidget(self.alignment_canvas, 1)

            alignment_layout.addWidget(alignment_graph_container, 3, 0, 1, 4)
            status_outer.addWidget(alignment_group)
            status_outer.addStretch(1)

            status_scroll = QScrollArea()
            status_scroll.setWidgetResizable(True)
            status_scroll.setFrameShape(QFrame.NoFrame)
            status_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            status_scroll.setWidget(status_panel)
            right_graph_layout.addWidget(status_scroll, 1)

            graph_splitter.addWidget(right_graph_column)
            self.parser.draw_plot(self.ax, "", POLARITY_LOWER_IS_MORE)
            self._redraw_alignment_plot()
            self.canvas.draw()
            graph_splitter.setSizes([1060, 350])

        self.left_content_panel = QWidget()
        left_content_layout = QHBoxLayout(self.left_content_panel)
        left_content_layout.setContentsMargins(0, 0, 0, 0)
        left_content_layout.setSpacing(0)
        left_content_layout.addWidget(graphs_panel, 1)

        self.show_log_edge_button = QPushButton("S\ne\nr\ni\na\nl\n \nL\no\ng")
        self.show_log_edge_button.setToolTip("Show serial log")
        self.show_log_edge_button.setFixedWidth(20)
        self.show_log_edge_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.show_log_edge_button.setVisible(False)
        self.show_log_edge_button.clicked.connect(self._show_log_panel)
        self.show_log_edge_button.setStyleSheet("padding: 6px 2px; font-size: 9px; font-weight: 700; color: #1f2f3d; background-color: #a9bac9; border: 1px solid #7f95a8; border-radius: 4px;")
        left_content_layout.addWidget(self.show_log_edge_button, 0)
        content_splitter.addWidget(self.left_content_panel)

        self._log_panel = self._make_panel_frame()
        log_panel = self._log_panel
        log_layout = QVBoxLayout(log_panel)
        log_header_top = QHBoxLayout()
        log_header_top.addWidget(QLabel("Serial log"))
        log_header_top.addStretch(1)
        self.pause_log_button = QPushButton("Pause")
        self.pause_log_button.setMinimumHeight(26)
        self.pause_log_button.setMinimumWidth(56)
        self.pause_log_button.setStyleSheet("padding: 3px 10px;")
        self.pause_log_button.clicked.connect(self._toggle_log_pause)
        log_header_top.addWidget(self.pause_log_button)
        collapse_button = QPushButton("▶")
        collapse_button.setToolTip("Collapse serial log")
        collapse_button.setMinimumHeight(26)
        collapse_button.setStyleSheet("padding: 3px 8px;")
        collapse_button.setMinimumWidth(34)
        collapse_button.clicked.connect(self._hide_log_panel)
        log_header_top.addWidget(collapse_button)
        log_layout.addLayout(log_header_top)

        log_header_bottom = QHBoxLayout()
        log_header_bottom.addStretch(1)
        save_log_button = QPushButton("Save log")
        save_log_button.setMinimumHeight(26)
        save_log_button.setMinimumWidth(72)
        save_log_button.setStyleSheet("padding: 3px 10px;")
        save_log_button.clicked.connect(self._save_log)
        log_header_bottom.addWidget(save_log_button)
        clear_log_button = QPushButton("Clear log")
        clear_log_button.setMinimumHeight(26)
        clear_log_button.setMinimumWidth(72)
        clear_log_button.setStyleSheet("padding: 3px 10px;")
        clear_log_button.clicked.connect(self._clear_log)
        log_header_bottom.addWidget(clear_log_button)
        log_layout.addLayout(log_header_bottom)
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        log_layout.addWidget(self.log_box)
        content_splitter.addWidget(log_panel)

        log_panel.setMinimumWidth(96)
        log_panel.setMaximumWidth(16777215)
        content_splitter.setSizes([1360, 180])

        self.resolution_status_label = QLabel("Window: 0 × 0 px")
        self.resolution_status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.resolution_status_label.setMinimumWidth(150)
        self.statusBar().addPermanentWidget(self.resolution_status_label)

        # shortcuts
        QShortcut(QKeySequence("S"), self, activated=lambda: self._send_command("START"))
        QShortcut(QKeySequence("X"), self, activated=lambda: self._send_command("STOP"))
        QShortcut(QKeySequence("F"), self, activated=lambda: self._send_command("FREE"))
        QShortcut(QKeySequence("H"), self, activated=lambda: self._send_command("HOME"))
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._save_csv)
        QShortcut(QKeySequence("Ctrl+P"), self, activated=self._save_png)

        self._load_settings()
        QTimer.singleShot(0, self._apply_persisted_ui_state)
        QTimer.singleShot(100, self._apply_persisted_ui_state)
        self._update_measurement_setup_summary()
        self._update_control_states()
        self._set_laser_button_state()
        self._set_position_button_states()
        self._refresh_status_labels()
        self._refresh_scan_list()
        self._update_resolution_indicator()
        self.statusBar().showMessage("Ready")


    def _apply_startup_window_layout(self):
        if self._startup_geometry_applied:
            return
        screen = self.screen() or QApplication.primaryScreen()
        if screen is None:
            self._startup_geometry_applied = True
            self._update_resolution_indicator()
            return

        available = screen.availableGeometry()

        # Fit to the actual usable laptop window area, not the nominal panel size.
        # Keep the window as large as practical, while reserving a small safety margin
        # so all regions remain visible on typical laptop screens.
        safe_margin_w = 12
        safe_margin_h = 12

        target_width = min(available.width() - safe_margin_w, 1880)
        target_height = min(available.height() - safe_margin_h, 1000)

        target_width = max(self.minimumWidth(), target_width)
        target_height = max(self.minimumHeight(), target_height)

        target_width = min(target_width, available.width() - 4)
        target_height = min(target_height, available.height() - 4)

        x = available.x() + max(0, (available.width() - target_width) // 2)
        y = available.y() + max(0, (available.height() - target_height) // 2)
        self.setGeometry(x, y, target_width, target_height)

        if self.content_splitter is not None:
            total_w = max(1, self.width())
            right_w = max(140, min(260, int(total_w * 0.10)))
            left_w = max(900, total_w - right_w)
            self.content_splitter.setSizes([left_w, right_w])


        if self.main_plot_splitter is not None:
            total_h = max(1, self.main_plot_splitter.height() or int(self.height() * 0.76))
            top_h = int(total_h * 0.40)
            mid_h = int(total_h * 0.38)
            bot_h = max(145, total_h - top_h - mid_h)
            self.main_plot_splitter.setSizes([top_h, mid_h, bot_h])

        self._startup_geometry_applied = True
        self._update_resolution_indicator()

    def _update_resolution_indicator(self):
        if self.resolution_status_label is None:
            return
        self.resolution_status_label.setText(f"Window: {self.width()} × {self.height()} px")

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_startup_window_layout()
        self._update_resolution_indicator()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_resolution_indicator()



    def _show_settings_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setMinimumWidth(420)
        layout = QVBoxLayout(dialog)

        info = QLabel(
            "Software settings are saved automatically when the application closes.\n\n"
            "They are stored in a JSON settings file placed in the same folder as the software.\n\n"
            "Current saved settings include serial port, diode model, signal polarity, output folder, notes, "
            "operator, diode type, diffuser used, bench configuration, test ID, scan speed, and return speed."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        dialog.exec()

    def _reset_all_settings(self):
        if self.port_combo is not None and self.port_combo.count() > 0:
            self.port_combo.setCurrentIndex(0)
        if self.diode_model_edit is not None:
            self.diode_model_edit.clear()
        for attr in ["operator_edit", "diode_type_edit", "diffuser_edit", "bench_config_edit", "test_id_edit"]:
            if hasattr(self, attr):
                getattr(self, attr).clear()
        if self.notes_edit is not None:
            self.notes_edit.clear()
        if self.output_folder_edit is not None:
            self.output_folder_edit.setText(str(Path.cwd()))
        if self.scan_speed_spin is not None:
            self.scan_speed_spin.setValue(8000)
        if self.return_speed_spin is not None:
            self.return_speed_spin.setValue(3000)
        if self.polarity_combo is not None:
            self.polarity_combo.setCurrentText(POLARITY_LOWER_IS_MORE)
        self._save_settings()
        self.statusBar().showMessage("Settings reset")

    def _find_best_alignment(self):
        # Placeholder for future motorised fine search. For now reset tracking and enter Free guidance mode.
        self._reset_peak()
        self._append_log("[alignment] Reset best alignment reading. Use Live and align to improve the reading.")
        self.statusBar().showMessage("Best alignment tracking reset")



    def _set_laser_button_state(self):
        if not hasattr(self, "laser_toggle_button") or self.laser_toggle_button is None:
            return
        if self.laser_manual_on:
            self.laser_toggle_button.setText("Laser Off")
            self.laser_toggle_button.setStyleSheet(BUTTON_LASER_ON_STYLE + " padding: 0 8px;")
            self.laser_toggle_button.setToolTip("Turn the laser off")
        else:
            self.laser_toggle_button.setText("Laser On")
            self.laser_toggle_button.setStyleSheet(BUTTON_NEUTRAL_STYLE + " padding: 0 8px;")
            self.laser_toggle_button.setToolTip("Laser is off")

    def _set_position_button_states(self):
        home_btn = self.control_buttons.get("HOME")
        end_btn = self.control_buttons.get("GOEND")
        state_styles = {
            "active": BUTTON_ACTIVE_STYLE,
            "moving": BUTTON_MOVING_STYLE,
            "inactive": BUTTON_NEUTRAL_STYLE,
        }
        if home_btn is not None:
            home_btn.setStyleSheet(state_styles.get(self.position_home_state, BUTTON_NEUTRAL_STYLE) + " padding: 0 8px;")
            if self.position_home_state == "moving":
                home_btn.setToolTip("Arm is moving to the home position")
            elif self.position_home_state == "active":
                home_btn.setToolTip("Arm is at the home position")
            else:
                home_btn.setToolTip("Move the arm to the home position")
        if end_btn is not None:
            end_btn.setStyleSheet(state_styles.get(self.position_end_state, BUTTON_NEUTRAL_STYLE) + " padding: 0 8px;")
            if self.position_end_state == "moving":
                end_btn.setToolTip("Arm is moving to the end position")
            elif self.position_end_state == "active":
                end_btn.setToolTip("Arm is at the end position")
            else:
                end_btn.setToolTip("Move the arm to the end position")

    def _line_indicates_home_sensor(self, line: str) -> bool:
        low = (line or "").lower()
        home_patterns = [
            "nullpoint reached",
            "already at nullpoint",
            "atnullpoint=1",
            "home sensor triggered",
            "home switch triggered",
            "photo diode breaker",
            "photodiode breaker",
            "photodiode triggered",
            "photo diode triggered",
            "breaker triggered",
            "home position reached",
        ]
        return any(pattern in low for pattern in home_patterns)

    def _trigger_home_stop_guard(self, source_line: str):
        if not self.connected or not self.home_stop_guard_armed:
            return
        self.home_stop_guard_armed = False
        self.position_home_state = "active"
        self.position_end_state = "inactive"
        self.current_scan_status = "Standby"
        self._set_position_button_states()
        try:
            self.worker.send("STOP")
            self._append_log(">>> STOP")
        except Exception:
            pass
        self.statusBar().showMessage("Home sensor detected, stopping at home position")
        self._append_log(f"[home] Home sensor detected from line: {source_line}")

    def _toggle_laser_manual(self):
        if not self.connected:
            QMessageBox.critical(self, APP_TITLE, "Connect to the Testbench first")
            return
        command = "LASER OFF" if self.laser_manual_on else "LASER ON"
        self._send_command(command)

    def _refresh_scan_list(self):
        if self.g1_current_check is not None:
            self.g1_current_check.blockSignals(True)
            self.g1_current_check.setText(self.current_scan_label)
            self.g1_current_check.setChecked(self.graph1_options.get("current", True))
            self.g1_current_check.setStyleSheet("")
            self.g1_current_check.blockSignals(False)
        if self.g1_ideal_check is not None:
            self.g1_ideal_check.blockSignals(True)
            self.g1_ideal_check.setChecked(self.graph1_options.get("ideal", True))
            self.g1_ideal_check.blockSignals(False)
        if self.g1_mirror_check is not None:
            self.g1_mirror_check.blockSignals(True)
            self.g1_mirror_check.setChecked(self.graph1_options.get("mirror", False))
            self.g1_mirror_check.blockSignals(False)
        if self.g1_grid_check is not None:
            self.g1_grid_check.blockSignals(True)
            self.g1_grid_check.setChecked(self.graph1_options.get("grid", True))
            self.g1_grid_check.blockSignals(False)
        if self.g1_error_band_check is not None:
            self.g1_error_band_check.blockSignals(True)
            self.g1_error_band_check.setChecked(self.graph1_options.get("error_band", False))
            self.g1_error_band_check.blockSignals(False)
        if self.g1_mode_combo is not None:
            self.g1_mode_combo.blockSignals(True)
            self.g1_mode_combo.setCurrentText(self.graph1_options.get("mode", "Normalised"))
            self.g1_mode_combo.blockSignals(False)
        if self.g2_ideal_check is not None:
            self.g2_ideal_check.blockSignals(True)
            self.g2_ideal_check.setChecked(self.graph2_options.get("ideal", True))
            self.g2_ideal_check.blockSignals(False)
        if self.g2_grid_check is not None:
            self.g2_grid_check.blockSignals(True)
            self.g2_grid_check.setChecked(self.graph2_options.get("grid", True))
            self.g2_grid_check.blockSignals(False)
        if self.g2_error_band_check is not None:
            self.g2_error_band_check.blockSignals(True)
            self.g2_error_band_check.setChecked(self.graph2_options.get("error_band", False))
            self.g2_error_band_check.blockSignals(False)
        if self.g2_mode_combo is not None:
            self.g2_mode_combo.blockSignals(True)
            self.g2_mode_combo.setCurrentText(self.graph2_options.get("mode", "Normalised"))
            self.g2_mode_combo.blockSignals(False)

        if self.compare_scan_list_widget is not None:
            self.compare_scan_list_widget.blockSignals(True)
            self.compare_scan_list_widget.clear()
            for idx, rec in enumerate(self.parser.scan_history):
                label = rec.label or f"Scan {idx + 1}"
                colour = rec.colour or self.scan_palette[idx % len(self.scan_palette)]
                item = QListWidgetItem(label)
                item.setIcon(self._scan_colour_icon(colour))
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item.setCheckState(Qt.Checked if self.scan_visibility.get(label, True) else Qt.Unchecked)
                item.setData(Qt.UserRole, f"__scan_{idx}")
                self.compare_scan_list_widget.addItem(item)
            show_current_item = bool(self.parser.samples) and (not self.current_scan_archived or self.graph2_options.get("current", True))
            if show_current_item:
                current_item = QListWidgetItem(self.current_scan_label)
                current_item.setIcon(self._scan_colour_icon(self._current_scan_colour()))
                current_item.setFlags(current_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                current_item.setCheckState(Qt.Checked if self.graph2_options.get("current", True) else Qt.Unchecked)
                current_item.setData(Qt.UserRole, "__g2_current__")
                self.compare_scan_list_widget.addItem(current_item)
            self.compare_scan_list_widget.blockSignals(False)
        self._update_scan_manager_buttons()

    def _sync_graph_options_from_controls(self, *_args):
        if self.g1_ideal_check is not None:
            self.graph1_options["ideal"] = self.g1_ideal_check.isChecked()
        if self.g1_current_check is not None:
            self.graph1_options["current"] = self.g1_current_check.isChecked()
        if self.g1_mirror_check is not None:
            self.graph1_options["mirror"] = self.g1_mirror_check.isChecked()
        if self.g1_grid_check is not None:
            self.graph1_options["grid"] = self.g1_grid_check.isChecked()
        if self.g1_error_band_check is not None:
            self.graph1_options["error_band"] = self.g1_error_band_check.isChecked()
        if self.g1_mode_combo is not None:
            self.graph1_options["mode"] = self.g1_mode_combo.currentText()
        if self.g2_ideal_check is not None:
            self.graph2_options["ideal"] = self.g2_ideal_check.isChecked()
        if self.g2_grid_check is not None:
            self.graph2_options["grid"] = self.g2_grid_check.isChecked()
        if self.g2_error_band_check is not None:
            self.graph2_options["error_band"] = self.g2_error_band_check.isChecked()
        if self.g2_mode_combo is not None:
            self.graph2_options["mode"] = self.g2_mode_combo.currentText()
        self._redraw_plot()

    def _on_scan_visibility_changed(self, *_args):
        if self.compare_scan_list_widget is not None:
            for i in range(self.compare_scan_list_widget.count()):
                item = self.compare_scan_list_widget.item(i)
                role = item.data(Qt.UserRole)
                checked = item.checkState() == Qt.Checked
                if role == "__g2_current__":
                    self.graph2_options["current"] = checked
                elif isinstance(role, str) and role.startswith("__scan_"):
                    try:
                        scan_idx = int(role.split("_")[-1])
                        if 0 <= scan_idx < len(self.parser.scan_history):
                            label = self.parser.scan_history[scan_idx].label or f"Scan {scan_idx + 1}"
                            self.scan_visibility[label] = checked
                    except Exception:
                        pass
        self._redraw_plot()

    def _selected_compare_scan_target(self):
        if self.compare_scan_list_widget is None:
            return None
        item = self.compare_scan_list_widget.currentItem()
        if item is None:
            return None
        role = item.data(Qt.UserRole)
        if role == "__g2_current__":
            return ("current", None)
        if not isinstance(role, str) or not role.startswith("__scan_"):
            return None
        try:
            return ("stored", int(role.split("_")[-1]))
        except Exception:
            return None

    def _update_scan_manager_buttons(self):
        target = self._selected_compare_scan_target()
        has_selection = False
        if target is not None:
            kind, idx = target
            has_selection = kind == "current" or (kind == "stored" and idx is not None and 0 <= idx < len(self.parser.scan_history))
        for button in [self.rename_scan_button, self.delete_scan_button]:
            if button is not None:
                button.setEnabled(has_selection)
        if self.clear_scans_button is not None:
            self.clear_scans_button.setEnabled(bool(self.parser.scan_history) or bool(self.parser.samples))

    def _rename_selected_scan(self):
        if self.compare_scan_list_widget is None:
            return
        item = self.compare_scan_list_widget.currentItem()
        if item is not None:
            self._rename_scan_from_item(item)

    def _delete_selected_scan(self):
        target = self._selected_compare_scan_target()
        if target is None:
            return
        kind, idx = target
        if kind == "current":
            self.parser.clear_measurement(preserve_history=True)
            self.current_scan_label = "Current scan"
            self.current_scan_archived = False
            self.home_stop_guard_armed = False
            self.graph1_options["current"] = False
            self.graph2_options["current"] = False
        elif idx is not None and 0 <= idx < len(self.parser.scan_history):
            old_label = self.parser.scan_history[idx].label or f"Scan {idx + 1}"
            del self.parser.scan_history[idx]
            self.scan_visibility.pop(old_label, None)
        self._refresh_scan_list()
        self._update_scan_manager_buttons()
        self._refresh_status_labels()
        self._redraw_plot()

    def _clear_stored_scans(self):
        self.parser.scan_history = []
        self.scan_visibility = {k: v for k, v in self.scan_visibility.items() if k == self.current_scan_label}
        if self.parser.samples:
            self.parser.clear_measurement(preserve_history=True)
            self.current_scan_label = "Current scan"
            self.graph1_options["current"] = False
            self.graph2_options["current"] = False
        self._refresh_scan_list()
        self._update_scan_manager_buttons()
        self._refresh_status_labels()
        self._redraw_plot()

    def _write_single_scan_csv(self, output_path, label, samples, diode_model="", interrupted=False):
        output = Path(output_path)
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["label", label])
            writer.writerow(["diode_model", diode_model])
            writer.writerow(["interrupted", interrupted])
            writer.writerow([])
            writer.writerow(["angle_deg", "voltage_v", "normalised_response"])
            norm = self.parser.normalised_voltages(self.polarity_combo.currentText(), samples)
            for sample, nval in zip(samples, norm):
                writer.writerow([f"{sample.angle_deg:.6f}", f"{sample.voltage:.6f}", f"{nval:.6f}"])

    def _export_selected_scan(self):
        target = self._selected_compare_scan_target()
        if target is None:
            return
        kind, idx = target
        if kind == "current":
            if not self.parser.samples:
                return
            label = self.current_scan_label
            samples = self.parser.samples
            diode_model = self.diode_model_edit.text().strip()
            interrupted = self.parser.state.interrupted
            default_name = self._sanitise_filename_piece(label) or "Current_scan"
        else:
            if idx is None or not (0 <= idx < len(self.parser.scan_history)):
                return
            record = self.parser.scan_history[idx]
            label = record.label or f"Scan_{idx + 1}"
            samples = record.samples
            diode_model = record.diode_model
            interrupted = record.interrupted
            default_name = self._sanitise_filename_piece(label) or f"Scan_{idx + 1}"
        default_path = str(Path(self.output_folder_edit.text().strip() or Path.cwd()) / f"{default_name}.csv")
        selected_path, _ = QFileDialog.getSaveFileName(self, "Export selected scan", default_path, "CSV Files (*.csv)")
        if not selected_path:
            return
        self._write_single_scan_csv(selected_path, label, samples, diode_model=diode_model, interrupted=interrupted)
        self.statusBar().showMessage(f"Exported {Path(selected_path).name}")

    def _hide_log_panel(self):
        if hasattr(self, "_log_panel") and self._log_panel is not None:
            self._log_panel.setVisible(False)
            if hasattr(self, "show_log_edge_button") and self.show_log_edge_button is not None:
                self.show_log_edge_button.setVisible(True)
                self.show_log_edge_button.raise_()
            self.statusBar().showMessage("Serial log hidden")
            if self.content_splitter is not None:
                self.content_splitter.setSizes([self.width() - 40, 0])

    def _show_log_panel(self):
        if hasattr(self, "_log_panel") and self._log_panel is not None:
            self._log_panel.setVisible(True)
            if hasattr(self, "show_log_edge_button") and self.show_log_edge_button is not None:
                self.show_log_edge_button.setVisible(False)
            self.statusBar().showMessage("Serial log shown")
            if self.content_splitter is not None:
                self.content_splitter.setSizes([self.width() - 150, 140])

    def _clear_session(self):
        self.parser.clear_measurement(preserve_history=False)
        self.alignment_history.clear()
        self.best_alignment_voltage = None
        self.best_reset_pending = False
        self.last_saved_file = None
        self.last_scan_duration_s = None
        self.current_scan_status = "Ready"
        self.laser_manual_on = False
        self.position_home_state = "inactive"
        self.position_end_state = "inactive"
        self._set_laser_button_state()
        self._set_position_button_states()

        self._refresh_scan_list()
        self._refresh_status_labels()
        self._redraw_plot()
        self._redraw_alignment_plot()
        self.statusBar().showMessage("Session cleared")
        self._append_log("[session] Cleared session")

    def _apply_speed_preset(self, scan_us, return_us, preset_name):
        self.scan_speed_spin.setValue(scan_us)
        self.return_speed_spin.setValue(return_us)
        self.statusBar().showMessage(f"{preset_name} preset loaded")
        self._append_log(f"[preset] {preset_name}: scan {scan_us} us, return {return_us} us")

    def _build_export_metadata(self):
        firmware = getattr(self, "_last_firmware_version", "")
        return {
            "operator": self.operator_edit.text().strip() if hasattr(self, "operator_edit") else "",
            "diode_type": self.diode_type_edit.text().strip() if hasattr(self, "diode_type_edit") else "",
            "diffuser_used": self.diffuser_edit.text().strip() if hasattr(self, "diffuser_edit") else "",
            "bench_configuration": self.bench_config_edit.text().strip() if hasattr(self, "bench_config_edit") else "",
            "test_id": self.test_id_edit.text().strip() if hasattr(self, "test_id_edit") else "",
            "firmware_version": firmware,
            "scan_duration_s": "" if self.last_scan_duration_s is None else f"{self.last_scan_duration_s:.2f}",
            "scan_status": self.current_scan_status,
        }


    def _export_report_set(self):
        if not self.parser.samples:
            QMessageBox.information(self, APP_TITLE, "No measurement data to export")
            return
        csv_path = self._suggest_output_path("csv")
        png_path = self._suggest_output_path("png")
        alignment_png_path = self._suggest_output_path("alignment.png")
        summary_txt_path = self._suggest_output_path("summary.txt")
        metadata = self._build_export_metadata()
        self.parser.save_csv(
            csv_path,
            self.diode_model_edit.text().strip(),
            self.polarity_combo.currentText(),
            self.notes_edit.text().strip() if self.notes_edit is not None else "",
            metadata,
        )
        if getattr(self, "figure", None) is not None:
            self.figure.savefig(png_path)
        else:
            self.parser.save_plot(png_path, self.diode_model_edit.text().strip(), self.polarity_combo.currentText())
        if getattr(self, "alignment_figure", None) is not None:
            self.alignment_figure.savefig(alignment_png_path)

        best_alignment_text = "--"
        if self.best_alignment_voltage is not None:
            best_alignment_text = f"{self.best_alignment_voltage:.4f} V"

        centre_text = self.centre_value_label.text().replace("Response at 0° (normalised): ", "") if hasattr(self, "centre_value_label") else "--"
        peak_offset_text = self.peak_angle_label.text().replace("Peak offset from 0° (max response): ", "") if hasattr(self, "peak_angle_label") else "--"
        duration_text = self.scan_duration_label.text().replace("Duration: ", "") if hasattr(self, "scan_duration_label") else "--"
        rmse_text = self.rmse_label.text().replace("RMSE (≤ 80°): ", "") if hasattr(self, "rmse_label") else "--"
        symmetry_text = self.symmetry_label.text().replace("Symmetry error (|+θ − −θ| mean): ", "") if hasattr(self, "symmetry_label") else "--"
        finished_text = self.scan_finished_label.text().replace("Finished: ", "") if hasattr(self, "scan_finished_label") else "--"

        summary_lines = [
            f"Diode model: {self.diode_model_edit.text().strip()}",
            f"Operator: {self.operator_edit.text().strip() if hasattr(self, 'operator_edit') else ''}",
            f"Scan date: {time.strftime('%d/%m/%Y %H:%M:%S')}",
            f"Samples: {self.parser.state.samples}/{self.parser.max_points}",
            f"RMSE (≤ 80°): {rmse_text}",
            f"Symmetry error (|+θ − −θ| mean): {symmetry_text}",
            f"Response at 0° (normalised): {centre_text}",
            f"Peak offset from 0° (max response): {peak_offset_text}",
            f"Best alignment reading: {best_alignment_text}",
            f"Finished: {finished_text}",
            f"Duration: {duration_text}",
        ]
        Path(summary_txt_path).write_text("\n".join(summary_lines), encoding="utf-8")
        self.last_saved_file = csv_path
        self._append_log(f"[export] Report set exported: {csv_path}, {png_path}, {alignment_png_path}, {summary_txt_path}")
        self.statusBar().showMessage("Report set exported")
        self._refresh_status_labels()


    def _queue_line(self, line: str):
        self.message_queue.put(("line", line))

    def _queue_status(self, status: str):
        self.message_queue.put(("status", status))

    def _selected_port_info(self):
        port_name = self.port_combo.currentText().strip() if self.port_combo is not None else ""
        if not port_name or serial is None:
            return None
        try:
            for p in serial.tools.list_ports.comports():
                if p.device == port_name:
                    return p
        except Exception:
            return None
        return None

    def _port_model_name(self, port_info):
        if port_info is None:
            return "--"
        hwid = str(getattr(port_info, "hwid", "") or "")
        description = str(getattr(port_info, "description", "") or "")
        product = str(getattr(port_info, "product", "") or "")
        manufacturer = str(getattr(port_info, "manufacturer", "") or "")
        if "VID:PID=1A86:7523" in hwid:
            return "Arduino compatible board (CH340)"
        for value in (product, description, manufacturer):
            if value:
                return value
        return str(getattr(port_info, "device", "--"))

    def _refresh_connected_device_panel(self):
        if self.device_model_label is not None:
            preferred_model = getattr(self, "_last_board_name", "--")
            if preferred_model and preferred_model != "--":
                self.device_model_label.setText(preferred_model)
            else:
                self.device_model_label.setText(self._port_model_name(self._connected_port_info))
        if self.device_port_label is not None:
            self.device_port_label.setText(getattr(self._connected_port_info, "device", "--") if self._connected_port_info is not None else "--")
        if self.device_hwid_label is not None:
            self.device_hwid_label.setText(getattr(self._connected_port_info, "hwid", "--") if self._connected_port_info is not None else "--")
        if self.device_manufacturer_label is not None:
            value = getattr(self._connected_port_info, "manufacturer", None) or getattr(self._connected_port_info, "description", None) or "--"
            self.device_manufacturer_label.setText(str(value))
        if self.device_firmware_label is not None:
            fw_text = getattr(self, "_last_firmware_version", "--") or "--"
            build_text = getattr(self, "_last_build_info", "--") or "--"
            if build_text != "--":
                self.device_firmware_label.setText(f"{fw_text}  |  {build_text}")
            else:
                self.device_firmware_label.setText(fw_text)
        if self.device_connected_at_label is not None:
            self.device_connected_at_label.setText(self._connected_at_text if self.connected else "--")

    def _refresh_ports(self):
        current = self.port_combo.currentText() if self.port_combo is not None else ""
        ports = []
        if serial is not None:
            ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo.clear()
        self.port_combo.addItems(ports)
        if current:
            idx = self.port_combo.findText(current)
            if idx >= 0:
                self.port_combo.setCurrentIndex(idx)
        self._refresh_connected_device_panel()

    def _toggle_connection(self):
        if not self.connected:
            port = self.port_combo.currentText().strip()
            if not port:
                QMessageBox.critical(self, APP_TITLE, "Select a serial port first")
                return
            try:
                self.worker.connect(port)
                self.connected = True
                self._connected_port_info = self._selected_port_info()
                self._connected_at_text = time.strftime("%d/%m/%Y %H:%M:%S")
                self.connect_button.setText("Disconnect")
                self.status_label.setText(f"● Connected to {port}")
                self.status_label.setStyleSheet("color: #1b7f1b;")
                self._append_log(f"Connected to {port}")
                self.statusBar().showMessage(f"Connected to {port}")
                self._refresh_connected_device_panel()
                self._request_speed_settings()
                QTimer.singleShot(400, self._request_firmware_info)
                self._save_settings()
            except Exception as exc:
                QMessageBox.critical(self, APP_TITLE, f"Could not connect: {exc}")
        else:
            self.worker.disconnect()
            self.connected = False
            self._connected_port_info = None
            self._connected_at_text = "--"
            self._last_firmware_version = "--"
            self._last_board_name = "--"
            self._last_build_info = "--"
            self.laser_manual_on = False
            self.position_home_state = "inactive"
            self.position_end_state = "inactive"
            self.home_stop_guard_armed = False
            self._set_laser_button_state()
            self._set_position_button_states()
            self.connect_button.setText("Connect")
            self.status_label.setText("○ Disconnected")
            self.status_label.setStyleSheet("color: #666666;")
            self._append_log("Disconnected")
            self.statusBar().showMessage("Disconnected")
            self._refresh_connected_device_panel()
            self._save_settings()
        self._update_control_states()

    def _send_command(self, command: str):
        if not self.connected:
            QMessageBox.critical(self, APP_TITLE, "Connect to the Testbench first")
            return
        try:
            self.worker.send(command)
            self._append_log(f">>> {command}")
            normalized_command = command.strip().upper()
            if normalized_command == "LASER ON":
                self.laser_manual_on = True
                self._set_laser_button_state()
            elif normalized_command == "LASER OFF":
                self.laser_manual_on = False
                self._set_laser_button_state()
            elif normalized_command in {"START", "FREE", "HOME", "GO END", "STOP"}:
                self.laser_manual_on = False
                self._set_laser_button_state()

            if normalized_command == "HOME":
                self.home_stop_guard_armed = True
                self.position_home_state = "moving"
                self.position_end_state = "inactive"
                self._set_position_button_states()
            elif normalized_command == "GO END":
                self.home_stop_guard_armed = False
                self.position_home_state = "inactive"
                self.position_end_state = "moving"
                self._set_position_button_states()
            elif normalized_command in {"START", "FREE", "STOP"}:
                self.home_stop_guard_armed = False
                self.position_home_state = "inactive"
                self.position_end_state = "inactive"
                self._set_position_button_states()
            if normalized_command == "FREE":
                self.alignment_history.clear()
                self.best_alignment_voltage = None
                self.best_reset_baseline = None
        except Exception as exc:
            QMessageBox.critical(self, APP_TITLE, f"Could not send command: {exc}")

    def _start_scan_sequence(self):
        count = 1
        if self.measurement_count_combo is not None:
            try:
                count = max(1, min(8, int(self.measurement_count_combo.currentText())))
            except Exception:
                count = 1

        # Preserve the current finished scan in Graph 2 before starting a new one.
        # Only Clear Plot or Clear Session should wipe comparison history.
        if self.parser.samples and not self.current_scan_archived:
            existing_label = (self.current_scan_label or "").strip()
            if existing_label and existing_label != "Current scan":
                archive_label = existing_label
            else:
                archive_label = self._next_unique_scan_label()
            self.parser.archive_current_scan(
                label=archive_label,
                diode_model=self.diode_model_edit.text().strip() if self.diode_model_edit is not None else "",
                colour=self._current_scan_colour(),
            )
            self.scan_visibility[archive_label] = True
            self._advance_scan_colour()

        self.series_total = count
        self.series_index = 0
        self.series_active = count > 1
        self.series_compare_mode = count > 1
        self.pending_auto_restart = False
        self.pending_sequence_label = None
        self.current_scan_label = "Current scan" if count == 1 else self._next_unique_scan_label()
        self.current_scan_archived = False
        self.home_stop_guard_armed = False
        self.graph1_options["current"] = True
        self.graph2_options["current"] = True
        self._refresh_scan_list()
        self._send_command("START")

    def _handle_auto_sequence_completion(self):
        if not self.series_active:
            return
        completed_label = self.current_scan_label or f"Scan {self.series_index + 1}"
        if self.series_compare_mode and self.parser.samples:
            self.parser.archive_current_scan(
                label=completed_label,
                diode_model=self.diode_model_edit.text().strip() if self.diode_model_edit is not None else "",
                colour=self._current_scan_colour(),
            )
            self.scan_visibility[completed_label] = True
            self._advance_scan_colour()
            self.current_scan_archived = True
        self.series_index += 1
        if self.series_index < self.series_total:
            next_index = self.series_index + 1
            self.pending_sequence_label = self._next_unique_scan_label()
            self.pending_auto_restart = True
            self._refresh_scan_list()
            self.statusBar().showMessage(f"Completed {completed_label}. Preparing {self.pending_sequence_label} of {self.series_total}")
        else:
            self.series_active = False
            self.series_total = 1
            self.series_index = 0
            self.pending_auto_restart = False
            self.pending_sequence_label = None
            if self.series_compare_mode:
                self.graph2_options["current"] = False
                self.current_scan_label = "Current scan"
            self.series_compare_mode = False
            self._refresh_scan_list()


    def _compare_scan(self):
        count = 1
        if self.measurement_count_combo is not None:
            try:
                count = max(1, min(8, int(self.measurement_count_combo.currentText())))
            except Exception:
                count = 1
        self.series_total = count
        self.series_index = 0
        self.series_active = count > 1
        self.series_compare_mode = True
        self.pending_auto_restart = False
        self.pending_sequence_label = None
        # Keep the existing current scan before starting compare sequence
        if self.parser.samples:
            if self.current_scan_label and self.current_scan_label != "Current scan":
                label = self.current_scan_label
            else:
                label = self._next_unique_scan_label()
            self.parser.archive_current_scan(label=label, diode_model=self.diode_model_edit.text().strip() if self.diode_model_edit is not None else "", colour=self._current_scan_colour())
            self.scan_visibility[label] = True
            self._advance_scan_colour()
        self.current_scan_label = self._next_unique_scan_label() if count > 1 else "Current scan"
        self.current_scan_archived = False
        self.home_stop_guard_armed = False
        self.graph1_options["current"] = True
        self.graph2_options["current"] = True
        self._refresh_scan_list()
        self._send_command("START")

    def _clear_measurement(self):
        self.parser.clear_measurement(preserve_history=False)
        self.scan_visibility = {}
        self.parser.scan_counter = 0
        self.best_alignment_voltage = None
        self.best_reset_pending = False
        self._refresh_scan_list()
        self._refresh_status_labels()
        self._redraw_plot()
        self._append_log("Measurement data cleared")

    def _current_scan_colour(self):
        return self.scan_palette[self.parser.scan_counter % len(self.scan_palette)]

    def _advance_scan_colour(self):
        self.parser.scan_counter += 1

    def _next_scan_label(self):
        return f"Scan {self.parser.scan_counter + 1}"

    def _existing_scan_labels(self):
        labels = []
        for idx, rec in enumerate(self.parser.scan_history, start=1):
            labels.append((rec.label or f"Scan {idx}").strip())
        if self.parser.samples and self.current_scan_label:
            labels.append(self.current_scan_label.strip())
        return labels

    def _next_unique_scan_label(self):
        used = set(self._existing_scan_labels())
        n = 1
        while f"Scan {n}" in used:
            n += 1
        return f"Scan {n}"

    def _scan_colour_icon(self, colour: str):
        pix = QPixmap(10, 10)
        pix.fill(Qt.transparent)
        from PySide6.QtGui import QPainter
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QColor("#666666"))
        painter.setBrush(QColor(colour))
        painter.drawRect(1, 1, 8, 8)
        painter.end()
        return QIcon(pix)

    def _browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select output folder", self.output_folder_edit.text())
        if folder:
            self.output_folder_edit.setText(folder)
            self._on_metadata_changed()

    def _sanitise_filename_piece(self, text: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", text.strip())
        return cleaned.strip("_")

    def _suggest_export_basename(self) -> str:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        diode_piece = self._sanitise_filename_piece(self.diode_model_edit.text()) if self.diode_model_edit is not None else ""
        base_name = f"cosine_response_{timestamp}"
        if diode_piece:
            base_name = f"{diode_piece}_{timestamp}"
        return base_name

    def _suggest_output_path(self, suffix: str) -> str:
        folder = Path(self.output_folder_edit.text().strip() or Path.cwd())
        folder.mkdir(parents=True, exist_ok=True)
        return str(folder / f"{self._suggest_export_basename()}.{suffix}")

    def _on_metadata_changed(self):
        if self.export_preview_label is not None:
            self.export_preview_label.setText(self._suggest_export_basename())
        self._update_measurement_setup_summary()
        self._save_settings()
        self._redraw_plot()

    def _reset_peak(self):
        self.best_alignment_voltage = None
        self.best_reset_pending = True
        self._refresh_status_labels()
        self.statusBar().showMessage("Best alignment reading reset")

    def _clear_log(self):
        if self.log_box is not None:
            self.log_box.clear()
        self.statusBar().showMessage("Serial log cleared")

    def _show_whats_new_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"What's new (V{APP_VERSION})")
        dialog.setMinimumWidth(520)
        layout = QVBoxLayout(dialog)

        title = QLabel(f"<b>What's new in V{APP_VERSION}</b>")
        title.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(title)

        intro = QLabel(
            "This final V26.7 release prepares the Cosine Response Test Bench Controller for executable packaging and public distribution."
        )
        intro.setWordWrap(True)
        intro.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(intro)

        bullet_points = [
            "Improved window responsiveness for laptop displays and smaller screen heights.",
            "Refined graph titles, labels, and comparison presentation for clearer scientific interpretation.",
            "Updated cosine error presentation and scan metrics wording.",
            "Improved scan comparison workflow, visibility controls, and export behaviour.",
            "Refined alignment controls and live trend display.",
            "Improved connection, device, and measurement setup presentation.",
            "General UI polish, stability improvements, and final release preparation updates.",
        ]
        bullet_html = "<br>".join([f"• {point}" for point in bullet_points])
        body = QLabel(bullet_html)
        body.setWordWrap(True)
        body.setTextFormat(Qt.RichText)
        body.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(body)

        button_row = QDialogButtonBox(QDialogButtonBox.Close)
        changelog_button = button_row.addButton("Full changelog", QDialogButtonBox.ActionRole)
        changelog_button.clicked.connect(self._open_full_changelog)
        button_row.rejected.connect(dialog.reject)
        layout.addWidget(button_row)
        dialog.exec()

    def _open_full_changelog(self):
        if 'QDesktopServices' in globals() and QDesktopServices.openUrl(QUrl(CHANGELOG_URL)):
            self.statusBar().showMessage("Opened full changelog")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Full changelog")
        dialog.setMinimumSize(640, 480)
        layout = QVBoxLayout(dialog)
        text = QPlainTextEdit(dialog)
        text.setReadOnly(True)
        text.setPlainText(
            "Cosine Response Test Bench Controller\n"
            "Fallback release changelog for V26.7\n\n"
            "V26.7 Final Release\n"
            "- Final executable release preparation\n"
            "- Report export summary corrected and aligned with live UI labels\n"
            "- What's New and About dialogs updated for release\n"
            "- Laptop fit and responsive layout refinements\n"
            "- Graph labelling, scan comparison, and metric wording polished\n"
            "- Alignment controls and export behaviour refined\n\n"
            "Earlier development history is available in the GitHub release changelog.\n"
            f"Release link: {CHANGELOG_URL}"
        )
        layout.addWidget(text)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()

    def _show_update_popup(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Updated to V{APP_VERSION}")
        dialog.setMinimumWidth(340)
        layout = QVBoxLayout(dialog)

        title = QLabel(f"<b>Updated to V{APP_VERSION}</b>")
        title.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(title)

        summary = QLabel("• Final release preparation and executable packaging updates<br>• Improved graph presentation, metrics wording, and export behaviour<br>• Better laptop fit and interface responsiveness")
        summary.setWordWrap(True)
        summary.setTextFormat(Qt.RichText)
        summary.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(summary)

        button_row = QDialogButtonBox()
        view_button = button_row.addButton("View details", QDialogButtonBox.ActionRole)
        close_button = button_row.addButton("Close", QDialogButtonBox.RejectRole)
        view_button.clicked.connect(lambda: (dialog.accept(), self._show_whats_new_dialog()))
        close_button.clicked.connect(dialog.reject)
        layout.addWidget(button_row)
        dialog.exec()

    def _maybe_show_update_popup(self):
        data = self._load_json_settings_data()
        last_seen_version = str(data.get("last_seen_whats_new_version", ""))
        if last_seen_version == APP_VERSION:
            return
        data["last_seen_whats_new_version"] = APP_VERSION
        self._save_json_settings_data(data)
        self._show_update_popup()

    def _show_about_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"About {APP_TITLE}")
        dialog.setMinimumWidth(440)
        layout = QVBoxLayout(dialog)

        title = QLabel(f"<div style='text-align:center;'><b>{APP_TITLE}</b></div>")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        body = QLabel(
            f"<div style='text-align:center;'>"
            f"<b>Version: {APP_VERSION}</b><br>"
            f"Release date: {APP_RELEASE_DATE}<br><br>"
            f"Developed by {APP_DEVELOPER}<br>"
            f"Nortcel Renewables<br>"
            f'GitHub: <a href="https://github.com/Nortcel/cosine-response-test-bench">github.com/Nortcel/cosine-response-test-bench</a><br>'
            f'Contact: <a href="mailto:info@nortcel.com">info@nortcel.com</a><br><br>'
            f"Purpose: Angular cosine response measurement and live sensor alignment.<br>"
            f"Licence: Open source release<br>"
            f"Firmware compatibility: Validated with Bench Firmware V5.2.2"
            f"</div>"
        )
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignCenter)
        body.setTextFormat(Qt.RichText)
        body.setTextInteractionFlags(Qt.TextBrowserInteraction | Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse | Qt.LinksAccessibleByKeyboard)
        body.setOpenExternalLinks(True)
        layout.addWidget(body)

        button_row = QDialogButtonBox(QDialogButtonBox.Ok)
        whats_new_button = button_row.addButton("What's new", QDialogButtonBox.ActionRole)
        changelog_button = button_row.addButton("Full changelog", QDialogButtonBox.ActionRole)
        whats_new_button.clicked.connect(self._show_whats_new_dialog)
        changelog_button.clicked.connect(self._open_full_changelog)
        button_row.accepted.connect(dialog.accept)
        layout.addWidget(button_row)
        dialog.exec()

    def _apply_speed_settings(self):
        if not self.connected:
            QMessageBox.information(self, APP_TITLE, "Connect to the Testbench first")
            return
        scan_us = int(self.scan_speed_spin.value()) if self.scan_speed_spin is not None else 600
        return_us = int(self.return_speed_spin.value()) if self.return_speed_spin is not None else 300
        try:
            self.worker.send(f"SET SCAN_US {scan_us}")
            self.worker.send(f"SET RETURN_US {return_us}")
            self._append_log(f">>> SET SCAN_US {scan_us}")
            self._append_log(f">>> SET RETURN_US {return_us}")
            self.statusBar().showMessage(f"Applied scan delay {scan_us} us and return delay {return_us} us")
            self._save_settings()
        except Exception as exc:
            QMessageBox.critical(self, APP_TITLE, f"Could not apply speed settings: {exc}")

    def _request_firmware_info(self):
        if not self.connected:
            return
        try:
            self._send_command("VERSION")
            QTimer.singleShot(250, lambda: self._send_command("INFO"))
        except Exception:
            pass

    def _request_speed_settings(self):
        if not self.connected:
            QMessageBox.critical(self, APP_TITLE, "Connect to the Testbench first")
            return
        self._send_command("GET SETTINGS")
        self._request_firmware_info()
        self.statusBar().showMessage("Requested firmware speed settings")

    def _load_settings(self):
        data = self._load_json_settings_data()
        port = data.get("serial_port", "")
        diode_model = data.get("diode_model", "")
        polarity = data.get("signal_polarity", POLARITY_LOWER_IS_MORE)
        output_folder = data.get("output_folder", str(Path.cwd()))
        notes = data.get("notes", "")
        operator_name = data.get("operator", "")
        diode_type = data.get("diode_type", "")
        diffuser = data.get("diffuser_used", "")
        bench_cfg = data.get("bench_configuration", "")
        test_id = data.get("test_id", "")
        scan_us = int(data.get("scan_us", 600))
        return_us = int(data.get("return_us", 300))

        if port and self.port_combo is not None:
            idx = self.port_combo.findText(port)
            if idx >= 0:
                self.port_combo.setCurrentIndex(idx)
        if self.diode_model_edit is not None:
            self.diode_model_edit.setText(str(diode_model))
        if self.polarity_combo is not None:
            idx = self.polarity_combo.findText(str(polarity))
            if idx >= 0:
                self.polarity_combo.setCurrentIndex(idx)
        if self.output_folder_edit is not None:
            self.output_folder_edit.setText(str(output_folder))
        if self.notes_edit is not None:
            self.notes_edit.setText(str(notes))
        if hasattr(self, "operator_edit") and self.operator_edit is not None:
            self.operator_edit.setText(str(operator_name))
            self.diode_type_edit.setText(str(diode_type))
            self.diffuser_edit.setText(str(diffuser))
            self.bench_config_edit.setText(str(bench_cfg))
            self.test_id_edit.setText(str(test_id))
        if self.scan_speed_spin is not None:
            self.scan_speed_spin.setValue(scan_us)
        if self.return_speed_spin is not None:
            self.return_speed_spin.setValue(return_us)

        # restore graph settings
        if hasattr(self, "g1_ideal_check") and self.g1_ideal_check is not None:
            self.g1_ideal_check.setChecked(bool(data.get("g1_ideal", True)))
        if hasattr(self, "g1_current_check") and self.g1_current_check is not None:
            self.g1_current_check.setChecked(bool(data.get("g1_current", True)))
        if hasattr(self, "g1_mirror_check") and self.g1_mirror_check is not None:
            self.g1_mirror_check.setChecked(bool(data.get("g1_mirror", False)))
        if hasattr(self, "g1_grid_check") and self.g1_grid_check is not None:
            self.g1_grid_check.setChecked(bool(data.get("g1_grid", True)))
        if hasattr(self, "g1_error_band_check") and self.g1_error_band_check is not None:
            self.g1_error_band_check.setChecked(bool(data.get("g1_error_band", False)))
        if hasattr(self, "g1_mode_combo") and self.g1_mode_combo is not None:
            mode = str(data.get("g1_mode", self.g1_mode_combo.currentText()))
            idx = self.g1_mode_combo.findText(mode)
            if idx >= 0:
                self.g1_mode_combo.setCurrentIndex(idx)

        if hasattr(self, "g2_ideal_check") and self.g2_ideal_check is not None:
            self.g2_ideal_check.setChecked(bool(data.get("g2_ideal", True)))
        if hasattr(self, "g2_grid_check") and self.g2_grid_check is not None:
            self.g2_grid_check.setChecked(bool(data.get("g2_grid", True)))
        if hasattr(self, "g2_error_band_check") and self.g2_error_band_check is not None:
            self.g2_error_band_check.setChecked(bool(data.get("g2_error_band", False)))
        if hasattr(self, "g2_mode_combo") and self.g2_mode_combo is not None:
            mode = str(data.get("g2_mode", self.g2_mode_combo.currentText()))
            idx = self.g2_mode_combo.findText(mode)
            if idx >= 0:
                self.g2_mode_combo.setCurrentIndex(idx)

        if hasattr(self, "trend_live_checkbox") and self.trend_live_checkbox is not None:
            self.trend_live_checkbox.setChecked(bool(data.get("alignment_trend_on", True)))
        if hasattr(self, "live_hold_combo") and self.live_hold_combo is not None:
            mode = str(data.get("live_value_mode", self.live_hold_combo.currentText()))
            idx = self.live_hold_combo.findText(mode)
            if idx >= 0:
                self.live_hold_combo.setCurrentIndex(idx)

        # store deferred restore state for after layout is built
        self._saved_window_width = int(data.get("window_width", self.width()))
        self._saved_window_height = int(data.get("window_height", self.height()))
        self._saved_is_maximized = bool(data.get("is_maximized", False))
        self._saved_content_splitter_sizes = data.get("content_splitter_sizes")
        self._saved_main_plot_splitter_sizes = data.get("main_plot_splitter_sizes")
        self._saved_graph_column_splitter_sizes = data.get("graph_column_splitter_sizes")
    def _save_settings(self):
        data = {}
        if self.port_combo is not None:
            data["serial_port"] = self.port_combo.currentText()
        if self.diode_model_edit is not None:
            data["diode_model"] = self.diode_model_edit.text()
        if self.polarity_combo is not None:
            data["signal_polarity"] = self.polarity_combo.currentText()
        if self.output_folder_edit is not None:
            data["output_folder"] = self.output_folder_edit.text()
        if self.notes_edit is not None:
            data["notes"] = self.notes_edit.text()
        if hasattr(self, "operator_edit") and self.operator_edit is not None:
            data["operator"] = self.operator_edit.text()
            data["diode_type"] = self.diode_type_edit.text()
            data["diffuser_used"] = self.diffuser_edit.text()
            data["bench_configuration"] = self.bench_config_edit.text()
            data["test_id"] = self.test_id_edit.text()
        if self.scan_speed_spin is not None:
            data["scan_us"] = self.scan_speed_spin.value()
        if self.return_speed_spin is not None:
            data["return_us"] = self.return_speed_spin.value()

        # window state
        data["window_width"] = self.width()
        data["window_height"] = self.height()
        data["is_maximized"] = self.isMaximized()

        # splitter sizes
        if hasattr(self, "content_splitter") and self.content_splitter is not None:
            data["content_splitter_sizes"] = list(self.content_splitter.sizes())
        if hasattr(self, "main_plot_splitter") and self.main_plot_splitter is not None:
            data["main_plot_splitter_sizes"] = list(self.main_plot_splitter.sizes())
        if hasattr(self, "graph_column_splitter") and self.graph_column_splitter is not None:
            data["graph_column_splitter_sizes"] = list(self.graph_column_splitter.sizes())

        # graph settings using actual widget names
        if hasattr(self, "g1_ideal_check") and self.g1_ideal_check is not None:
            data["g1_ideal"] = self.g1_ideal_check.isChecked()
        if hasattr(self, "g1_current_check") and self.g1_current_check is not None:
            data["g1_current"] = self.g1_current_check.isChecked()
        if hasattr(self, "g1_mirror_check") and self.g1_mirror_check is not None:
            data["g1_mirror"] = self.g1_mirror_check.isChecked()
        if hasattr(self, "g1_grid_check") and self.g1_grid_check is not None:
            data["g1_grid"] = self.g1_grid_check.isChecked()
        if hasattr(self, "g1_error_band_check") and self.g1_error_band_check is not None:
            data["g1_error_band"] = self.g1_error_band_check.isChecked()
        if hasattr(self, "g1_mode_combo") and self.g1_mode_combo is not None:
            data["g1_mode"] = self.g1_mode_combo.currentText()

        if hasattr(self, "g2_ideal_check") and self.g2_ideal_check is not None:
            data["g2_ideal"] = self.g2_ideal_check.isChecked()
        if hasattr(self, "g2_grid_check") and self.g2_grid_check is not None:
            data["g2_grid"] = self.g2_grid_check.isChecked()
        if hasattr(self, "g2_error_band_check") and self.g2_error_band_check is not None:
            data["g2_error_band"] = self.g2_error_band_check.isChecked()
        if hasattr(self, "g2_mode_combo") and self.g2_mode_combo is not None:
            data["g2_mode"] = self.g2_mode_combo.currentText()

        if hasattr(self, "trend_live_checkbox") and self.trend_live_checkbox is not None:
            data["alignment_trend_on"] = self.trend_live_checkbox.isChecked()
        if hasattr(self, "live_hold_combo") and self.live_hold_combo is not None:
            data["live_value_mode"] = self.live_hold_combo.currentText()

        self._save_json_settings_data(data)



    def _save_csv(self):
        if not self.parser.samples:
            QMessageBox.information(self, APP_TITLE, "No measurement data to save")
            return
        default_path = self._suggest_output_path("csv")
        selected_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", default_path, "CSV Files (*.csv)")
        if not selected_path:
            return
        try:
            self.parser.save_csv(selected_path, self.diode_model_edit.text().strip(), self.polarity_combo.currentText(), self.notes_edit.text().strip() if self.notes_edit is not None else "")
            self.last_saved_file = selected_path
            self._append_log(f"[save] CSV saved to {selected_path}")
            self._refresh_status_labels()
        except Exception as exc:
            QMessageBox.critical(self, APP_TITLE, f"Could not save CSV: {exc}")

    def _save_png(self):
        if not self.parser.samples:
            QMessageBox.information(self, APP_TITLE, "No measurement data to save")
            return
        default_path = self._suggest_output_path("png")
        selected_path, _ = QFileDialog.getSaveFileName(self, "Save PNG", default_path, "PNG Files (*.png)")
        if not selected_path:
            return
        try:
            if getattr(self, "figure", None) is not None:
                self.figure.savefig(selected_path)
            else:
                self.parser.save_plot(selected_path, self.diode_model_edit.text().strip(), self.polarity_combo.currentText())
            self.last_saved_file = selected_path
            self._append_log(f"[save] PNG saved to {selected_path}")
            self._refresh_status_labels()
        except Exception as exc:
            QMessageBox.critical(self, APP_TITLE, f"Could not save PNG: {exc}")

    def _process_queue(self):
        processed_any = False
        processed_count = 0
        max_per_tick = 25
        try:
            while processed_count < max_per_tick:
                msg_type, payload = self.message_queue.get_nowait()
                processed_any = True
                processed_count += 1
                if msg_type == "status":
                    self.status_label.setText(payload)
                    self._append_log(f"[status] {payload}")
                    self.statusBar().showMessage(payload)
                else:
                    self._append_log(payload)

                    upper_payload = payload.strip().upper()
                    if upper_payload.startswith("CONFIG: SCAN_US="):
                        try:
                            value = int(payload.split("=", 1)[1].strip())
                            if hasattr(self, "scan_speed_spin") and self.scan_speed_spin is not None:
                                self.scan_speed_spin.setValue(value)
                        except Exception:
                            pass
                    elif (
                        upper_payload.startswith("FIRMWARE=")
                        or upper_payload.startswith("VERSION=")
                        or upper_payload.startswith("FW_VERSION=")
                        or upper_payload.startswith("FW=")
                    ):
                        try:
                            self._last_firmware_version = payload.split("=", 1)[1].strip()
                            self._refresh_connected_device_panel()
                        except Exception:
                            pass
                    elif upper_payload.startswith("BOARD="):
                        try:
                            self._last_board_name = payload.split("=", 1)[1].strip()
                            self._refresh_connected_device_panel()
                        except Exception:
                            pass
                    elif upper_payload.startswith("BUILD=") or upper_payload.startswith("BUILD_DATE=") or upper_payload.startswith("BUILD_TIME="):
                        try:
                            value = payload.split("=", 1)[1].strip()
                            if upper_payload.startswith("BUILD="):
                                self._last_build_info = value
                            elif upper_payload.startswith("BUILD_DATE="):
                                current = getattr(self, "_last_build_info", "--")
                                if current == "--" or not current:
                                    self._last_build_info = value
                                else:
                                    self._last_build_info = f"{value} {current}".strip()
                            elif upper_payload.startswith("BUILD_TIME="):
                                current = getattr(self, "_last_build_info", "--")
                                if current == "--" or not current:
                                    self._last_build_info = value
                                else:
                                    self._last_build_info = f"{current} {value}".strip()
                            self._refresh_connected_device_panel()
                        except Exception:
                            pass
                    elif upper_payload.startswith("RETURN_US="):
                        try:
                            value = int(payload.split("=", 1)[1].strip())
                            if hasattr(self, "return_speed_spin") and self.return_speed_spin is not None:
                                self.return_speed_spin.setValue(value)
                        except Exception:
                            pass
                    elif upper_payload.startswith("ATNULLPOINT="):
                        try:
                            is_home = payload.split("=", 1)[1].strip() == "1"
                            self.position_home_state = "active" if is_home else "inactive"
                            if is_home:
                                self.position_end_state = "inactive"
                            self._set_position_button_states()
                        except Exception:
                            pass

                    low_payload = payload.lower()

                    if "measurement started" in low_payload:
                        self.scan_start_monotonic = time.monotonic()
                        self.current_scan_status = "Running"
                        self.laser_manual_on = False
                        self._set_laser_button_state()
                        if not self.series_active and self.series_total == 1 and self.current_scan_label == "Current scan":
                            self.current_scan_label = "Current scan"
                    elif "measurement complete" in low_payload:
                        if self.scan_start_monotonic is not None:
                            self.last_scan_duration_s = time.monotonic() - self.scan_start_monotonic
                        self.current_scan_status = "Completed"
                        self.laser_manual_on = False
                        self._set_laser_button_state()
                        self.last_scan_finished_at = time.strftime("%d/%m/%Y %H:%M:%S")
                    elif "measurement stopped" in low_payload or "right end sensor triggered" in low_payload:
                        if self.scan_start_monotonic is not None:
                            self.last_scan_duration_s = time.monotonic() - self.scan_start_monotonic
                        self.current_scan_status = "Incomplete"
                        self.laser_manual_on = False
                        self._set_laser_button_state()
                        self.last_scan_finished_at = time.strftime("%d/%m/%Y %H:%M:%S")

                    if "laser on" in low_payload:
                        self.laser_manual_on = True
                        self._set_laser_button_state()
                    elif (
                        "laser off" in low_payload
                        or "moving to end position" in low_payload
                        or "end position reached" in low_payload
                        or "move to end stopped" in low_payload
                        or "nullpoint reached" in low_payload
                        or "already at nullpoint" in low_payload
                    ):
                        self.laser_manual_on = False
                        self._set_laser_button_state()

                    if self._line_indicates_home_sensor(payload):
                        self._trigger_home_stop_guard(payload)

                    if "end position reached" in low_payload or "moving to end position" in low_payload:
                        self.position_home_state = "inactive"
                        self.position_end_state = "active" if "reached" in low_payload else "moving"
                        self._set_position_button_states()
                    elif "nullpoint reached" in low_payload or "already at nullpoint" in low_payload or self._line_indicates_home_sensor(payload):
                        self.home_stop_guard_armed = False
                        self.position_home_state = "active"
                        self.position_end_state = "inactive"
                        self._set_position_button_states()
                    elif "measurement started" in low_payload or "free mode active" in low_payload:
                        self.home_stop_guard_armed = False
                        self.position_home_state = "inactive"
                        self.position_end_state = "inactive"
                        self._set_position_button_states()

                    prev_live = self.parser.state.live_voltage_v
                    self.parser.feed_line(payload)
                    current_live = self.parser.state.live_voltage_v
                    if current_live is not None and self.parser.state.mode in ("Free", "Measuring"):
                        if not self.alignment_history or prev_live != current_live:
                            self.alignment_history.append(current_live)
                    if self.pending_auto_restart and ("nullpoint reached" in low_payload or "already at nullpoint" in low_payload or self._line_indicates_home_sensor(payload) or ("mode=standby" in low_payload and self.parser.state.mode == "Standby")):
                        self.pending_auto_restart = False
                        self.current_scan_label = self.pending_sequence_label or self.current_scan_label
                        self.pending_sequence_label = None
                        self.current_scan_archived = False
                        self.home_stop_guard_armed = False
                        QTimer.singleShot(250, lambda: self._send_command("START"))
        except queue.Empty:
            pass

        if processed_any:
            self._refresh_status_labels()
            self._redraw_plot()
            self._redraw_alignment_plot()
            self._update_control_states()
            if self.parser.scan_completed and self.series_active and self.parser.state.mode == "Standby":
                self.parser.scan_completed = False
                self._handle_auto_sequence_completion()


    def _refresh_status_labels(self):
        display_mode = str(self.parser.state.mode or "Idle")
        self.mode_label.setText(f"Mode: {display_mode.upper()}")
        if self.controls_status_label is not None:
            status_text = self.parser.state.mode
            if self.series_active:
                status_text = f"Scanning {self.series_index + 1} of {self.series_total}"
            self.controls_status_label.setText("")
        temp_text = "--" if self.parser.state.temperature_c is None else f"{self.parser.state.temperature_c:.1f} °C"
        humidity_text = "--" if self.parser.state.humidity_percent is None else f"{self.parser.state.humidity_percent:.1f} %"

        voltage_v = self.parser.state.live_voltage_v
        display_voltage = voltage_v
        if hasattr(self, "live_hold_combo") and voltage_v is not None and self.alignment_history:
            mode = self.live_hold_combo.currentText()
            values = list(self.alignment_history)
            if mode == "5 sample average" and len(values) >= 1:
                display_voltage = sum(values[-5:]) / min(5, len(values))
            elif mode == "10 sample average" and len(values) >= 1:
                display_voltage = sum(values[-10:]) / min(10, len(values))
        live_voltage_text = "--" if display_voltage is None else f"{display_voltage:.5f} V"

        temp_suffix = "" if str(temp_text).strip().endswith("°C") else " °C"
        self.temp_label.setText(f"Temperature: {temp_text}{temp_suffix}")
        if hasattr(self, "temp_gauge") and self.temp_gauge is not None:
            self.temp_gauge.setValueFloat(self.parser.state.temperature_c)
        self.humidity_label.setText(f"Humidity: {humidity_text}")
        if hasattr(self, "humidity_gauge") and self.humidity_gauge is not None:
            self.humidity_gauge.setValueFloat(self.parser.state.humidity_percent)
        status_text = self.current_scan_status
        if self.parser.state.interrupted:
            status_text = "Interrupted"
        elif self.series_active:
            status_text = f"Sequence {self.series_index + 1} of {self.series_total}"
        self.samples_label.setText(f"Status: {status_text}")
        self.samples_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.progress_bar.setValue(self.parser.state.samples)
        if hasattr(self, "progress_value_label") and self.progress_value_label is not None:
            self.progress_value_label.setText(f"{self.parser.state.samples}/{self.parser.max_points}")

        polarity_mode = self.polarity_combo.currentText() if self.polarity_combo is not None else POLARITY_LOWER_IS_MORE

        if voltage_v is not None:
            current_v = voltage_v
            if self.best_alignment_voltage is None or self.best_reset_pending:
                self.best_alignment_voltage = current_v
                self.best_reset_pending = False
            else:
                if polarity_mode == POLARITY_LOWER_IS_MORE:
                    self.best_alignment_voltage = min(self.best_alignment_voltage, current_v)
                else:
                    self.best_alignment_voltage = max(self.best_alignment_voltage, current_v)


        rmse_value = self.parser.calculate_rmse(polarity_mode)
        self.rmse_label.setText("RMSE (≤ 80°): --" if rmse_value is None else f"RMSE (≤ 80°): {rmse_value:.4f}")

        symmetry_value = self.parser.calculate_symmetry_error(polarity_mode)
        self.symmetry_label.setText("Symmetry error (|+θ − −θ| mean): --" if symmetry_value is None else f"Symmetry error (|+θ − −θ| mean): {symmetry_value:.4f}")

        self.scan_finished_label.setText(f"Finished: {self.last_scan_finished_at if self.last_scan_finished_at else '--'}")
        self.scan_duration_label.setText("Duration: --" if self.last_scan_duration_s is None else f"Duration: {self.last_scan_duration_s:.1f} s")

        centre_val = "--"
        peak_angle = "--"
        if self.parser.samples:
            nearest_idx = min(range(len(self.parser.samples)), key=lambda i: abs(self.parser.samples[i].angle_deg))
            centre_norm = self.parser.normalised_voltages(polarity_mode)
            if centre_norm and nearest_idx < len(centre_norm):
                centre_val = f"{centre_norm[nearest_idx]:.4f}"
            else:
                centre_val = "--"
            norm_vals = self.parser.normalised_voltages(polarity_mode)
            if norm_vals:
                peak_idx = max(range(len(norm_vals)), key=lambda i: norm_vals[i])
                peak_sample = self.parser.samples[peak_idx]
                peak_angle = f"{peak_sample.angle_deg:.2f}°"
        self.centre_value_label.setText(f"Response at 0° (normalised): {centre_val}")
        self.peak_angle_label.setText(f"Peak offset from 0° (max response): {peak_angle}")

        diode_name = self.diode_model_edit.text().strip() if self.diode_model_edit is not None else ""
        rmse_txt = "--" if rmse_value is None else f"{rmse_value:.4f}"
        sym_txt = "--" if symmetry_value is None else f"{symmetry_value:.4f}"
        if hasattr(self, "scan_summary_label") and self.scan_summary_label is not None:
            self.scan_summary_label.setText("")
        if hasattr(self, "scan_summary_secondary_label") and self.scan_summary_secondary_label is not None:
            self.scan_summary_secondary_label.setText("")
            self.scan_summary_secondary_label.setVisible(False)

        if self.alignment_bar is not None:
            if display_voltage is None:
                self.alignment_bar.setValue(None)
                self.alignment_bar.setBestValue(None)
                self.alignment_bar.setFormat("-- V")
                if polarity_mode == POLARITY_LOWER_IS_MORE:
                    self.alignment_scale_label.setText("Signal Voltage | Best: --")
                else:
                    self.alignment_scale_label.setText("Signal Voltage | Best: --")
            else:
                voltage_mv = max(0, min(5000, int(round(display_voltage * 1000.0))))
                best_mv = None
                if self.best_alignment_voltage is not None:
                    best_mv = max(0, min(5000, int(round(self.best_alignment_voltage * 1000.0))))
                if polarity_mode == POLARITY_LOWER_IS_MORE:
                    display_value = 5000 - voltage_mv
                    display_best = None if best_mv is None else 5000 - best_mv
                    self.alignment_bar.setInvertedAppearance(True)
                else:
                    display_value = voltage_mv
                    display_best = best_mv
                    self.alignment_bar.setInvertedAppearance(False)
                best_text = "--" if self.best_alignment_voltage is None else f"{self.best_alignment_voltage:.4f} V"
                self.alignment_scale_label.setText(f"Signal Voltage | Best: {best_text}")
                self.alignment_bar.setValue(display_value)
                self.alignment_bar.setBestValue(display_best)
                self.alignment_bar.setFormat(f"{display_voltage:.4f} V")

    def _redraw_alignment_plot(self):
        if self.alignment_ax is None or self.alignment_canvas is None:
            return
        self.alignment_ax.clear()
        self.alignment_figure.subplots_adjust(left=0.14, right=0.97, top=0.88, bottom=0.22)
        self.alignment_ax.set_xlabel("Recent samples")
        self.alignment_ax.set_ylabel("Signal voltage (V)")
        self.alignment_ax.grid(True, alpha=0.35)

        if self.trend_live_checkbox is not None and not self.trend_live_checkbox.isChecked():
            self.alignment_ax.text(0.5, 0.5, "Trend paused", ha="center", va="center", transform=self.alignment_ax.transAxes)
            self.alignment_canvas.draw()
            return

        values = list(self.alignment_history)
        if values:
            mode = self.live_hold_combo.currentText() if self.live_hold_combo is not None else "Raw live value"
            plot_vals = values[:]
            if mode == "5 sample average":
                plot_vals = [sum(values[max(0, i - 4):i + 1]) / len(values[max(0, i - 4):i + 1]) for i in range(len(values))]
            elif mode == "10 sample average":
                plot_vals = [sum(values[max(0, i - 9):i + 1]) / len(values[max(0, i - 9):i + 1]) for i in range(len(values))]

            max_samples = 101
            plot_vals = plot_vals[-max_samples:]
            if len(plot_vals) == 1:
                x_vals = [1]
            else:
                step = (max_samples - 1) / (len(plot_vals) - 1)
                x_vals = [1 + i * step for i in range(len(plot_vals))]
            self.alignment_ax.plot(x_vals, plot_vals, color="#1f77b4")
            if self.best_alignment_voltage is not None:
                try:
                    best_val = max(plot_vals) if self.polarity_combo.currentText() == POLARITY_HIGHER_IS_MORE else min(plot_vals)
                    idx = plot_vals.index(best_val)
                    self.alignment_ax.plot([x_vals[idx]], [plot_vals[idx]], marker="o", markersize=7, linestyle="None", color="#ff7f0e")
                except Exception:
                    pass
            ymin = min(plot_vals)
            ymax = max(plot_vals)
            if ymin == ymax:
                ymin -= 0.1
                ymax += 0.1
            pad = max((ymax - ymin) * 0.08, 0.02)
            self.alignment_ax.set_ylim(ymin - pad, ymax + pad)

            self.alignment_ax.set_xlim(1, max_samples)
            ticks = list(range(1, max_samples + 1, 10))
            if ticks[-1] != max_samples:
                ticks.append(max_samples)
            self.alignment_ax.set_xticks(ticks)
        self.alignment_canvas.draw()

    def _plot_curve_with_mode(self, ax, samples, polarity_mode, colour, label, mode, show_markers=True, linestyle="-", alpha=1.0):
        if not samples:
            return None
        angles = [s.angle_deg for s in samples]
        marker = "o" if show_markers else None
        if mode == "Raw voltage":
            values = [s.voltage for s in samples]
            ax.plot(angles, values, marker=marker, linewidth=1.2, markersize=3.2, color=colour, label=label, linestyle=linestyle, alpha=alpha)
            return values
        values = self.parser.normalised_voltages(polarity_mode, samples)
        ax.plot(angles, values, marker=marker, linewidth=1.2, markersize=3.2, color=colour, label=label, linestyle=linestyle, alpha=alpha)
        return values

    def _configure_graph_axis(self, ax, mode, title, grid_on):
        ax.set_title(title)
        ax.set_xlabel("Angle of Incidence (°)")
        ax.set_xlim(-100, 100)
        if mode == "Raw voltage":
            ax.set_ylabel("Raw voltage (V)")
        else:
            ax.set_ylabel("Normalised Response (−)")
            ax.set_ylim(0, 1.05)
        if grid_on:
            ax.grid(True, linestyle=(0, (1, 4)), linewidth=0.8, alpha=0.9)
        else:
            ax.grid(False)
        self._set_common_angle_markers(ax)

    def _raw_voltage_limits(self, samples):
        if not samples:
            return (0.0, 1.0)
        vals = [s.voltage for s in samples]
        lo = min(vals)
        hi = max(vals)
        pad = max((hi - lo) * 0.08, 0.02)
        if lo == hi:
            lo -= 0.1
            hi += 0.1
        return (lo - pad, hi + pad)

    def _update_control_states(self):
        mode = self.parser.state.mode
        measuring = mode == "Measuring"
        free_mode = mode == "Free"

        if "START" in self.control_buttons:
            self.control_buttons["START"].setEnabled(self.connected and not measuring and not free_mode)
        if "FREE" in self.control_buttons:
            self.control_buttons["FREE"].setEnabled(self.connected and not measuring and not free_mode)
        if hasattr(self, "stop_live_button") and self.stop_live_button is not None:
            stop_live_enabled = self.connected and free_mode
            self.stop_live_button.setEnabled(stop_live_enabled)
            self.stop_live_button.setStyleSheet((BUTTON_ACTIVE_STYLE if stop_live_enabled else BUTTON_DISABLED_STYLE) + " padding: 0 10px;")
        if "HOME" in self.control_buttons:
            self.control_buttons["HOME"].setEnabled(self.connected and not measuring)
        if "STOP" in self.control_buttons:
            self.control_buttons["STOP"].setEnabled(self.connected and (measuring or free_mode))
        if "STATUS" in self.control_buttons:
            self.control_buttons["STATUS"].setEnabled(self.connected)
        if "LASERON" in self.control_buttons:
            self.control_buttons["LASERON"].setEnabled(self.connected and not measuring and not free_mode)
            self._set_laser_button_state()
        if "GOEND" in self.control_buttons:
            self.control_buttons["GOEND"].setEnabled(self.connected and not measuring and not free_mode)
        self._set_position_button_states()

    def _on_polarity_changed(self):
        self.best_alignment_voltage = None
        self.best_reset_pending = False
        self._refresh_status_labels()
        self._redraw_plot()
        self._redraw_alignment_plot()

    def _redraw_plot(self):
        if self.ax is None or self.figure is None:
            return

        self.ax.clear()
        if getattr(self, "_main_right_ax", None) is not None:
            try:
                self._main_right_ax.remove()
            except Exception:
                pass
            self._main_right_ax = None
        if getattr(self, "_compare_right_ax", None) is not None:
            try:
                self._compare_right_ax.remove()
            except Exception:
                pass
            self._compare_right_ax = None
        if getattr(self, "_error_right_ax", None) is not None:
            try:
                self._error_right_ax.remove()
            except Exception:
                pass
            self._error_right_ax = None
        if self.compare_ax is not None:
            self.compare_ax.clear()
        if self.error_ax is not None:
            self.error_ax.clear()

        title = self.diode_model_edit.text().strip() if self.diode_model_edit is not None else ""
        polarity_mode = self.polarity_combo.currentText() if self.polarity_combo is not None else POLARITY_LOWER_IS_MORE
        ideal_x, ideal_y = self.parser.ideal_cosine_curve()

        # Graph 1: Cosine Response always visible
        g1_mode = self.graph1_options.get("mode", "Normalised")
        self._configure_graph_axis(self.ax, g1_mode, f"Graph 1: Cosine Response of {title}" if title else "Graph 1: Cosine Response", self.graph1_options.get("grid", True))
        if self.graph1_options.get("ideal", True):
            if g1_mode == "Raw voltage" and self.parser.samples:
                low, high = self._raw_voltage_limits(self.parser.samples)
                self.ax.set_ylim(low, high)
                dark = self.parser._dark_offset(polarity_mode)
                ref = self.parser._reference_voltage(polarity_mode)
                if polarity_mode == POLARITY_LOWER_IS_MORE:
                    ideal_raw = [dark - max(0.0, y) * max(dark - ref, 1e-9) for y in ideal_y]
                else:
                    ideal_raw = [dark + max(0.0, y) * max(ref - dark, 1e-9) for y in ideal_y]
                self.ax.plot(ideal_x, ideal_raw, label="Ideal Cosine (cos θ)", linewidth=2.0, color="#1f77b4")
            else:
                self.ax.plot(ideal_x, ideal_y, label="Ideal Cosine (cos θ)", linewidth=2.0, color="#1f77b4")

        if self.parser.samples and self.graph1_options.get("current", True):
            current_colour = self._current_scan_colour()
            angles = [s.angle_deg for s in self.parser.samples]
            values = self._plot_curve_with_mode(self.ax, self.parser.samples, polarity_mode, current_colour, self.current_scan_label, g1_mode)
            if self.graph1_options.get("mirror", False):
                mirror_values = self.parser.normalised_voltages(polarity_mode) if g1_mode != "Raw voltage" else [s.voltage for s in self.parser.samples]
                self.ax.plot([-a for a in angles], mirror_values, linestyle="--", linewidth=1.0, alpha=0.6, color=current_colour, label="Mirrored Curve")
            if self.graph1_options.get("error_band", False) and self.graph1_options.get("ideal", True) and g1_mode != "Raw voltage":
                self.ax.fill_between(angles, values, [max(0.0, math.cos(math.radians(a))) for a in angles], color=current_colour, alpha=0.12)
        self._main_right_ax = None if g1_mode == "Raw voltage" else self._make_right_voltage_axis(self.ax, self.parser.samples if self.parser.samples else None, polarity_mode)
        g1_handles, g1_labels = self.ax.get_legend_handles_labels()
        if any(label and not str(label).startswith("_") for label in g1_labels):
            self.ax.legend(loc="upper left", fontsize=8)

        # Graph 2: Cosine Response Comparison always visible
        g2_mode = self.graph2_options.get("mode", "Normalised")
        self._configure_graph_axis(self.compare_ax, g2_mode, "Graph 2: Cosine Response Scan Comparison", self.graph2_options.get("grid", True))
        if self.graph2_options.get("ideal", True) and g2_mode != "Raw voltage":
            self.compare_ax.plot(ideal_x, ideal_y, linewidth=2.0, color="#1f77b4", label="Ideal Cosine (cos θ)")

        compare_records = []
        for idx, rec in enumerate(self.parser.scan_history, start=1):
            label = rec.label or f"Scan {idx}"
            if self.scan_visibility.get(label, True):
                compare_records.append((label, rec.samples, rec.colour or self.scan_palette[(idx - 1) % len(self.scan_palette)]))
        if self.parser.samples and self.graph2_options.get("current", True):
            compare_records.append((self.current_scan_label, self.parser.samples, self._current_scan_colour()))

        first_samples_for_axis = None
        for idx, (label, samples, colour) in enumerate(compare_records):
            if not samples:
                continue
            if first_samples_for_axis is None:
                first_samples_for_axis = samples
                if self.graph2_options.get("ideal", True) and g2_mode == "Raw voltage":
                    low, high = self._raw_voltage_limits(samples)
                    self.compare_ax.set_ylim(low, high)
                    dark = self.parser._dark_offset(polarity_mode)
                    ref = self.parser._reference_voltage(polarity_mode)
                    if polarity_mode == POLARITY_LOWER_IS_MORE:
                        ideal_raw = [dark - max(0.0, y) * max(dark - ref, 1e-9) for y in ideal_y]
                    else:
                        ideal_raw = [dark + max(0.0, y) * max(ref - dark, 1e-9) for y in ideal_y]
                    self.compare_ax.plot(ideal_x, ideal_raw, linewidth=2.0, color="#1f77b4", label="Ideal Cosine (cos θ)")
            values = self._plot_curve_with_mode(self.compare_ax, samples, polarity_mode, colour, label, g2_mode, show_markers=True)
            if self.graph2_options.get("error_band", False) and self.graph2_options.get("ideal", True) and g2_mode != "Raw voltage":
                angles = [s.angle_deg for s in samples]
                self.compare_ax.fill_between(angles, values, [max(0.0, math.cos(math.radians(a))) for a in angles], color=colour, alpha=0.08)
        if first_samples_for_axis is None and self.parser.samples:
            first_samples_for_axis = self.parser.samples
        compare_count = len(compare_records)
        self._compare_right_ax = None
        if g2_mode != "Raw voltage" and compare_count <= 1:
            self._compare_right_ax = self._make_right_voltage_axis(
                self.compare_ax,
                first_samples_for_axis if first_samples_for_axis is not None else None,
                polarity_mode,
            )
        g2_handles, g2_labels = self.compare_ax.get_legend_handles_labels()
        if any(label and not str(label).startswith("_") for label in g2_labels):
            self.compare_ax.legend(loc="upper left", fontsize=8)

        # Cosine Error always visible
        self.error_ax.axhline(0, linestyle="--", linewidth=1.0, color="#666666")
        self.error_ax.set_title("Cosine Error")
        self.error_ax.set_xlabel("Angle of Incidence (°)")
        self.error_ax.set_ylabel("Error (%)")
        if self.graph1_options.get("grid", True):
            self.error_ax.grid(True, alpha=0.35)
        else:
            self.error_ax.grid(False)
        self.error_ax.set_xlim(-100, 100)
        self.error_ax.set_ylim(-30.0, 30.0)
        self._set_common_angle_markers(self.error_ax)
        if self.parser.samples and self.graph1_options.get("current", True):
            angles = [s.angle_deg for s in self.parser.samples]
            norm = self.parser.normalised_voltages(polarity_mode)
            errs = [(n - max(0.0, math.cos(math.radians(a)))) * 100.0 for a, n in zip(angles, norm)]
            self.error_ax.plot(angles, errs, marker="o", linewidth=1.2, markersize=3, color=self._current_scan_colour(), label=self.current_scan_label)
        self._error_right_ax = self._make_error_alignment_axis(self.error_ax, polarity_mode)
        handles, labels = self.error_ax.get_legend_handles_labels()
        if handles:
            self.error_ax.legend(loc="upper left", fontsize=8)

        if self.compare_canvas is not None:
            self.compare_canvas.show()
        if self.error_canvas is not None:
            self.error_canvas.show()
        if self.main_plot_splitter is not None:
            if not getattr(self, "_session_splitter_initialised", False):
                self.main_plot_splitter.setSizes([400, 500, 170])
                self._session_splitter_initialised = True

        self._apply_figure_layouts()
        self.canvas.draw()
        if self.compare_canvas is not None:
            self.compare_canvas.draw()
        if self.error_canvas is not None:
            self.error_canvas.draw()
        self._refresh_scan_list()


    def _export_graph1_selected(self):
        if self.graph1_export_png_check is None or self.graph1_export_csv_check is None:
            return
        do_png = self.graph1_export_png_check.isChecked()
        do_csv = self.graph1_export_csv_check.isChecked()
        if not (do_png or do_csv):
            QMessageBox.information(self, APP_TITLE, "Select at least one Graph 1: Cosine Response export option")
            return
        if do_png:
            self._export_graph1_png()
        if do_csv:
            self._export_graph1_csv()

    def _export_graph2_selected(self):
        if self.graph2_export_png_check is None or self.graph2_export_csv_check is None:
            return
        do_png = self.graph2_export_png_check.isChecked()
        do_csv = self.graph2_export_csv_check.isChecked()
        do_avg_csv = self.graph2_export_avg_csv_check.isChecked() if self.graph2_export_avg_csv_check is not None else False
        if not (do_png or do_csv or do_avg_csv):
            QMessageBox.information(self, APP_TITLE, "Select at least one Graph 2: Cosine Response Comparison export option")
            return
        if do_png:
            self._export_graph2_png()
        if do_csv:
            self._export_graph2_csv()
        if do_avg_csv:
            self._export_graph2_average_csv()

    def _export_error_selected(self):
        if self.error_export_png_check is None or self.error_export_csv_check is None:
            return
        do_png = self.error_export_png_check.isChecked()
        do_csv = self.error_export_csv_check.isChecked()
        if not (do_png or do_csv):
            QMessageBox.information(self, APP_TITLE, "Select at least one Cosine Error export option")
            return
        if do_png:
            self._export_error_png()
        if do_csv:
            self._export_error_csv()

    def _export_graph1_png(self):
        if not self.parser.samples:
            QMessageBox.information(self, APP_TITLE, "No current scan to export")
            return
        default_path = self._suggest_output_path("graph1.png")
        selected_path, _ = QFileDialog.getSaveFileName(self, "Export Graph 1: Cosine Response as PNG", default_path, "PNG Files (*.png)")
        if selected_path:
            self.figure.savefig(selected_path, dpi=160)
            self.statusBar().showMessage(f"Saved {Path(selected_path).name}")

    def _export_graph1_csv(self):
        if not self.parser.samples:
            QMessageBox.information(self, APP_TITLE, "No current scan to export")
            return
        default_path = self._suggest_output_path("graph1.csv")
        selected_path, _ = QFileDialog.getSaveFileName(self, "Export Graph 1: Cosine Response as CSV", default_path, "CSV Files (*.csv)")
        if selected_path:
            self._write_scan_csv(Path(selected_path), [(self.current_scan_label, self.parser.samples)], include_only_visible=False)

    def _export_graph2_png(self):
        default_path = self._suggest_output_path("graph2.png")
        selected_path, _ = QFileDialog.getSaveFileName(self, "Export Graph 2: Cosine Response Comparison as PNG", default_path, "PNG Files (*.png)")
        if selected_path:
            self.compare_figure.savefig(selected_path, dpi=160)
            self.statusBar().showMessage(f"Saved {Path(selected_path).name}")

    def _graph2_visible_records(self):
        visible_records = []
        for idx, rec in enumerate(self.parser.scan_history, start=1):
            label = rec.label or f"Scan {idx}"
            if self.scan_visibility.get(label, True):
                visible_records.append((label, rec.samples))
        if self.parser.samples and self.graph2_options.get("current", True):
            visible_records.append((self.current_scan_label, self.parser.samples))
        return visible_records

    def _export_graph2_csv(self):
        visible_records = self._graph2_visible_records()
        if not visible_records:
            QMessageBox.information(self, APP_TITLE, "No visible Graph 2: Cosine Response Comparison scans to export")
            return
        default_path = self._suggest_output_path("graph2.csv")
        selected_path, _ = QFileDialog.getSaveFileName(self, "Export Graph 2: Cosine Response Comparison as CSV", default_path, "CSV Files (*.csv)")
        if selected_path:
            self._write_scan_csv(Path(selected_path), visible_records, include_only_visible=True)

    def _export_graph2_average_csv(self):
        visible_records = self._graph2_visible_records()
        if not visible_records:
            QMessageBox.information(self, APP_TITLE, "No visible Graph 2: Cosine Response Comparison scans to average")
            return
        default_path = self._suggest_output_path("graph2_average.csv")
        selected_path, _ = QFileDialog.getSaveFileName(self, "Export Graph 2: Cosine Response Comparison average as CSV", default_path, "CSV Files (*.csv)")
        if selected_path:
            self._write_graph2_average_csv(Path(selected_path), visible_records)

    def _export_error_png(self):
        if not self.parser.samples:
            QMessageBox.information(self, APP_TITLE, "No cosine error graph to export")
            return
        default_path = self._suggest_output_path("cosine_error.png")
        selected_path, _ = QFileDialog.getSaveFileName(self, "Export Cosine Error as PNG", default_path, "PNG Files (*.png)")
        if selected_path:
            self.error_figure.savefig(selected_path, dpi=160)
            self.statusBar().showMessage(f"Saved {Path(selected_path).name}")

    def _export_error_csv(self):
        if not self.parser.samples:
            QMessageBox.information(self, APP_TITLE, "No cosine error data to export")
            return
        default_path = self._suggest_output_path("cosine_error.csv")
        selected_path, _ = QFileDialog.getSaveFileName(self, "Export Cosine Error as CSV", default_path, "CSV Files (*.csv)")
        if selected_path:
            self._write_error_csv(Path(selected_path))

    def _write_scan_csv(self, output: Path, records, include_only_visible: bool = False):
        polarity_mode = self.polarity_combo.currentText() if self.polarity_combo is not None else POLARITY_LOWER_IS_MORE
        diode_model = self.diode_model_edit.text().strip() if self.diode_model_edit is not None else ""
        notes = self.notes_edit.text().strip() if self.notes_edit is not None else ""
        metadata = self._build_export_metadata()

        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)

            writer.writerow(["metadata", "value"])
            writer.writerow(["diode_model", diode_model])
            writer.writerow(["signal_polarity", polarity_mode])
            writer.writerow(["measurement_notes", notes])
            writer.writerow(["operator", metadata.get("operator", "")])
            writer.writerow(["diode_type", metadata.get("diode_type", "")])
            writer.writerow(["diffuser_used", metadata.get("diffuser_used", "")])
            writer.writerow(["bench_configuration", metadata.get("bench_configuration", "")])
            writer.writerow(["test_id", metadata.get("test_id", "")])
            writer.writerow(["firmware_version", metadata.get("firmware_version", "")])
            writer.writerow(["scan_duration_s", metadata.get("scan_duration_s", "")])
            writer.writerow(["scan_status", metadata.get("scan_status", "")])
            writer.writerow(["temperature_c", "" if self.parser.state.temperature_c is None else f"{self.parser.state.temperature_c:.6f}"])
            writer.writerow(["humidity_percent", "" if self.parser.state.humidity_percent is None else f"{self.parser.state.humidity_percent:.6f}"])
            writer.writerow(["scan_completed", 1 if self.current_scan_status == "Completed" else 0])
            writer.writerow(["scan_interrupted", 1 if self.parser.state.interrupted else 0])
            writer.writerow(["export_scope", "displayed_scans_only" if include_only_visible else "current_scan"])
            writer.writerow([])

            per_scan_details = []
            headers = []
            for rec_idx, (label, samples) in enumerate(records, start=1):
                safe_label = label.strip() if label else f"Scan {rec_idx}"
                dark_offset = self.parser._dark_offset(polarity_mode)
                reference_voltage = self.parser._reference_voltage(polarity_mode)
                corrected_values = self.parser.corrected_voltages(polarity_mode)
                normalised_values = self.parser.normalised_voltages(polarity_mode, samples)
                # correct values must be derived from the provided samples, not the current parser.samples
                original_samples = self.parser.samples
                self.parser.samples = samples
                try:
                    dark_offset = self.parser._dark_offset(polarity_mode)
                    reference_voltage = self.parser._reference_voltage(polarity_mode)
                    corrected_values = self.parser.corrected_voltages(polarity_mode)
                    normalised_values = self.parser.normalised_voltages(polarity_mode, samples)
                finally:
                    self.parser.samples = original_samples

                ideal_values = [max(0.0, math.cos(math.radians(s.angle_deg))) for s in samples]
                per_scan_details.append((safe_label, samples, dark_offset, reference_voltage, corrected_values, normalised_values, ideal_values))
                headers.extend([
                    f"{safe_label} sample",
                    f"{safe_label} angle_deg",
                    f"{safe_label} voltage_v",
                    f"{safe_label} dark_offset_v",
                    f"{safe_label} reference_voltage_v",
                    f"{safe_label} corrected_voltage_v",
                    f"{safe_label} normalised_voltage",
                    f"{safe_label} ideal_cosine",
                ])
            writer.writerow(headers)

            max_len = max((len(samples) for _, samples, *_rest in per_scan_details), default=0)
            for row_idx in range(max_len):
                row = []
                for _label, samples, dark_offset, reference_voltage, corrected_values, normalised_values, ideal_values in per_scan_details:
                    if row_idx < len(samples):
                        sample = samples[row_idx]
                        row.extend([
                            row_idx + 1,
                            f"{sample.angle_deg:.6f}",
                            f"{sample.voltage:.6f}",
                            f"{dark_offset:.6f}",
                            f"{reference_voltage:.6f}",
                            f"{corrected_values[row_idx]:.6f}" if row_idx < len(corrected_values) else "",
                            f"{normalised_values[row_idx]:.6f}" if row_idx < len(normalised_values) else "",
                            f"{ideal_values[row_idx]:.6f}" if row_idx < len(ideal_values) else "",
                        ])
                    else:
                        row.extend(["", "", "", "", "", "", "", ""])
                writer.writerow(row)

        self.statusBar().showMessage(f"Saved {output.name}")

    def _write_graph2_average_csv(self, output: Path, records):
        polarity_mode = self.polarity_combo.currentText() if self.polarity_combo is not None else POLARITY_LOWER_IS_MORE
        averaged = {}
        for label, samples in records:
            norm = self.parser.normalised_voltages(polarity_mode, samples)
            for sample, nval in zip(samples, norm):
                key = round(sample.angle_deg, 6)
                averaged.setdefault(key, []).append(nval)
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["angle_deg", "average_normalised_response", "scan_count"])
            for angle in sorted(averaged.keys()):
                values = averaged[angle]
                writer.writerow([f"{angle:.6f}", f"{(sum(values)/len(values)):.6f}", len(values)])
        self.statusBar().showMessage(f"Saved {output.name}")

    def _write_error_csv(self, output: Path):
        polarity_mode = self.polarity_combo.currentText() if self.polarity_combo is not None else POLARITY_LOWER_IS_MORE
        angles = [s.angle_deg for s in self.parser.samples]
        norm = self.parser.normalised_voltages(polarity_mode)
        errs = [(n - max(0.0, math.cos(math.radians(a)))) * 100.0 for a, n in zip(angles, norm)]
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["label", self.current_scan_label])
            writer.writerow(["angle_deg", "measured_minus_ideal"])
            for angle, err in zip(angles, errs):
                writer.writerow([f"{angle:.6f}", f"{err:.6f}"])
        self.statusBar().showMessage(f"Saved {output.name}")


    def _choose_scan_style(self, current_name, current_colour):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit scan")
        dialog.setMinimumWidth(320)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        form = QGridLayout()
        form.setHorizontalSpacing(8)
        form.setVerticalSpacing(8)
        form.addWidget(QLabel("Scan label"), 0, 0)
        name_edit = QLineEdit(current_name)
        form.addWidget(name_edit, 0, 1)
        form.addWidget(QLabel("Colour"), 1, 0)
        colour_preview = QLabel("    ")
        colour_preview.setMinimumWidth(36)
        colour_preview.setStyleSheet(f"background-color: {current_colour}; border: 1px solid #888; border-radius: 3px;")
        choose_button = QPushButton("Change colour")
        chosen = {"value": current_colour}

        def pick_colour():
            colour = QColorDialog.getColor(QColor(chosen["value"]), dialog, "Choose scan colour")
            if colour.isValid():
                chosen["value"] = colour.name()
                colour_preview.setStyleSheet(f"background-color: {chosen['value']}; border: 1px solid #888; border-radius: 3px;")

        choose_button.clicked.connect(pick_colour)
        colour_row = QHBoxLayout()
        colour_row.setContentsMargins(0, 0, 0, 0)
        colour_row.addWidget(colour_preview)
        colour_row.addWidget(choose_button)
        colour_row.addStretch(1)
        form.addLayout(colour_row, 1, 1)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.Accepted:
            return None
        new_name = name_edit.text().strip() or current_name
        return new_name, chosen["value"]



    def _rename_scan_from_item(self, item):
        try:
            role = item.data(Qt.UserRole) if item is not None else None
            if role == "__g2_current__":
                current_name = self.current_scan_label
                current_colour = self._current_scan_colour()
                result = self._choose_scan_style(current_name, current_colour)
                if result is not None:
                    new_label, new_colour = result
                    self.current_scan_label = new_label
                    try:
                        current_index = self.parser.scan_counter % len(self.scan_palette)
                        self.scan_palette[current_index] = new_colour
                    except Exception:
                        pass
                    self._refresh_scan_list()
                    self._redraw_plot()
                return
            if not isinstance(role, str) or not role.startswith("__scan_"):
                return
            row = int(role.split("_")[-1])
            if row < 0 or row >= len(self.parser.scan_history):
                return
            record = self.parser.scan_history[row]
            current_name = record.label or item.text()
            current_colour = record.colour or self.scan_palette[row % len(self.scan_palette)]
            result = self._choose_scan_style(current_name, current_colour)
            if result is not None:
                old_label = record.label or current_name
                new_label, new_colour = result
                record.label = new_label
                record.colour = new_colour
                self.scan_visibility[new_label] = self.scan_visibility.pop(old_label, item.checkState() == Qt.Checked)
                self._refresh_scan_list()
                self._redraw_plot()
        except Exception as exc:
            QMessageBox.warning(self, APP_TITLE, f"Edit error: {exc}")

    def _make_right_voltage_axis(self, axis, samples, polarity_mode):
        raw_ticks = self.parser.raw_voltage_ticks(polarity_mode, samples=samples)
        if not raw_ticks:
            norm_ticks = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
            if polarity_mode == POLARITY_LOWER_IS_MORE:
                raw_ticks = list(zip(norm_ticks, [5.00, 4.80, 4.60, 4.40, 4.20, 4.00]))
            else:
                raw_ticks = list(zip(norm_ticks, [0.00, 0.20, 0.40, 0.60, 0.80, 1.00]))
        right_ax = axis.twinx()
        right_ax.set_ylim(axis.get_ylim())
        right_ax.set_yticks([tick for tick, _ in raw_ticks])
        right_ax.set_yticklabels([f"{value:.2f}" for _, value in raw_ticks])
        right_ax.set_ylabel("Raw voltage (V)", labelpad=10)
        right_ax.grid(False)
        return right_ax

    def _set_common_angle_markers(self, axis):
        axis.axvline(0, linestyle="--", linewidth=1.0, color="#5fa3e3")
        for x, style in [(-90, "--"), (-80, ":"), (80, ":"), (90, "--")]:
            axis.axvline(x, linestyle=style, linewidth=1, color="#5fa3e3", alpha=0.9)
        tick_positions = [-100, -90, -80, -50, -25, 0, 25, 50, 80, 90, 100]
        axis.set_xticks(tick_positions)
        axis.set_xticklabels([str(v) for v in tick_positions])

    def _make_error_alignment_axis(self, axis, polarity_mode):
        right_ax = axis.twinx()
        right_ax.set_ylim(axis.get_ylim())
        right_ax.set_yticks([t for t in axis.get_yticks()])
        right_ax.set_yticklabels(["" for _ in axis.get_yticks()])
        right_ax.set_ylabel(" ", labelpad=10)
        right_ax.tick_params(axis="y", length=0)
        right_ax.grid(False)
        for spine in right_ax.spines.values():
            spine.set_visible(False)
        return right_ax

    def _apply_figure_layouts(self):
        try:
            if getattr(self, "figure", None) is not None:
                self.figure.subplots_adjust(left=0.065, right=0.90, top=0.88, bottom=0.17)
            if getattr(self, "compare_figure", None) is not None:
                self.compare_figure.subplots_adjust(left=0.065, right=0.90, top=0.88, bottom=0.17)
            if getattr(self, "error_figure", None) is not None:
                self.error_figure.subplots_adjust(left=0.065, right=0.90, top=0.88, bottom=0.22)
        except Exception:
            pass

    def _toggle_log_pause(self):
        self.log_paused = not self.log_paused
        if hasattr(self, "pause_log_button") and self.pause_log_button is not None:
            self.pause_log_button.setText("Resume" if self.log_paused else "Pause")
        self.statusBar().showMessage("Serial log paused" if self.log_paused else "Serial log resumed")

    def _save_log(self):
        if self.log_box is None:
            return
        default_path = str(Path(self.output_folder_edit.text().strip() or Path.cwd()) / f"{self._suggest_export_basename()}_serial_log.txt")
        selected_path, _ = QFileDialog.getSaveFileName(self, "Save serial log", default_path, "Text Files (*.txt)")
        if not selected_path:
            return
        Path(selected_path).write_text(self.log_box.toPlainText(), encoding="utf-8")
        self.statusBar().showMessage(f"Saved {Path(selected_path).name}")

    def _append_log(self, text: str):
        if self.log_box is not None and not self.log_paused:
            self.log_box.appendPlainText(text)
            scrollbar = self.log_box.verticalScrollBar()
            if scrollbar is not None:
                scrollbar.setValue(scrollbar.maximum())


    def _show_help_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("How to use")
        dialog.setMinimumWidth(460)
        layout = QVBoxLayout(dialog)

        title = QLabel("<b>Quick start</b>")
        title.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(title)

        help_text = QLabel(
            "1. Select the COM port and click Connect.<br><br>"
            "<b>Running a measurement</b><br>"
            "Choose the number of scans, then click Start Scan. Use Stop Scan to interrupt the current run.<br><br>"
            "<b>Understanding the graphs</b><br>"
            "Graph 1: Cosine Response shows the current scan. Graph 2: Cosine Response Comparison compares stored scans. Cosine Error shows deviation from the ideal cosine.<br><br>"
            "<b>Exporting data</b><br>"
            "Use the Export scan panels next to each graph. Exports follow the items currently shown.<br><br>"
            "<b>Alignment mode</b><br>Live and Stop now sit together for quick setup checks, with current and best values shown more clearly.<br><br>"
            "Use Live and the live trend to check alignment. Lower voltage means stronger alignment when lower voltage polarity is selected."
        )
        help_text.setWordWrap(True)
        help_text.setTextFormat(Qt.RichText)
        help_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(help_text)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        dialog.exec()


    def _apply_persisted_ui_state(self):
        try:
            if hasattr(self, "_saved_window_width") and hasattr(self, "_saved_window_height"):
                if not getattr(self, "_saved_is_maximized", False):
                    self.resize(self._saved_window_width, self._saved_window_height)

            if hasattr(self, "_saved_content_splitter_sizes") and self._saved_content_splitter_sizes and self.content_splitter is not None:
                self.content_splitter.setSizes([int(v) for v in self._saved_content_splitter_sizes])

            if hasattr(self, "_saved_graph_column_splitter_sizes") and self._saved_graph_column_splitter_sizes and self.graph_column_splitter is not None:
                self.graph_column_splitter.setSizes([int(v) for v in self._saved_graph_column_splitter_sizes])

            if hasattr(self, "_saved_main_plot_splitter_sizes") and self._saved_main_plot_splitter_sizes and self.main_plot_splitter is not None:
                self.main_plot_splitter.setSizes([int(v) for v in self._saved_main_plot_splitter_sizes])

            if getattr(self, "_saved_is_maximized", False):
                self.showMaximized()

            self._sync_graph_options_from_controls()
        except Exception:
            pass

    def closeEvent(self, event):
        try:
            self._save_settings()
            self.worker.disconnect()
        except Exception:
            pass
        super().closeEvent(event)


def write_error_log(message: str):
    try:
        Path(ERROR_LOG_FILE).write_text(message, encoding="utf-8")
    except Exception:
        pass


def main(argv: Optional[Sequence[str]] = None) -> int:
    try:
        if QApplication is None:
            print("PySide6 is not installed. Install it with: pip install PySide6 pyserial matplotlib", file=sys.stderr)
            return 1
        app = QApplication(list(argv) if argv is not None else list(sys.argv))
        window = BenchMainWindow()
        window.show()
        return app.exec()
    except Exception:
        error_text = traceback.format_exc()
        write_error_log(error_text)
        print(error_text, file=sys.stderr)
        try:
            if QApplication is not None:
                app = QApplication.instance() or QApplication(list(argv) if argv is not None else list(sys.argv))
                QMessageBox.critical(None, APP_TITLE, f"Startup failed. Details were written to {ERROR_LOG_FILE}")
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    exit_code = main()
    if exit_code not in (0, None):
        print(f"Application exited with code {exit_code}", file=sys.stderr)