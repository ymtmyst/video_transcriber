import os
from pathlib import Path
from PySide6.QtCore import Qt, QUrl, Slot
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView

os.environ.setdefault("QT_WEBENGINE_CHROMIUM_FLAGS", "--enable-transparent-visuals")

class TransparentOverlay(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.webview = QWebEngineView()
        self.webview.page().setBackgroundColor(Qt.GlobalColor.transparent)
        self.setCentralWidget(self.webview)

        root_dir = Path(__file__).resolve().parents[2]
        html_path = root_dir / "ui" / "index.html"
        if html_path.exists():
            self.webview.load(QUrl.fromLocalFile(str(html_path)))
        else:
            self.webview.setHtml("<h1 style='color:red;'>ui/index.html not found!</h1>")

        screen = QApplication.primaryScreen()
        if screen is not None:
            self.setGeometry(screen.geometry())

    @Slot()
    def show_recording_state(self) -> None:
        self.webview.page().runJavaScript("window.showRecordingUI && window.showRecordingUI()")

    @Slot()
    def hide_recording_state(self) -> None:
        self.webview.page().runJavaScript("window.hideRecordingUI && window.hideRecordingUI()")

    @Slot(float)
    def update_level(self, level: float) -> None:
        # print(f"DEBUG: Overlay received level: {level:.4f}")
        js = f"window.updateWaveform && window.updateWaveform({float(level)})"
        self.webview.page().runJavaScript(js)
