import sys
from pathlib import Path
import os

# Ensure 'src' is on sys.path so existing modules (utils, config) resolve
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# On some Windows environments, Qt fails to set PER_MONITOR_AWARE_V2 by default.
# Force a safer DPI awareness to avoid the access denied warning.
os.environ.setdefault("QT_QPA_PLATFORM", "windows:dpiawareness=1")

from PySide6.QtWidgets import QApplication
from ui.overlay import TransparentOverlay
from core.stt_controller import STTController
from utils.audio_utils import AudioRecorder


def select_microphone() -> int | None:
    print("マイクデバイスを検索中...")
    devices = AudioRecorder.list_audio_devices()
    if not devices:
        print("有効なマイクが見つかりませんでした。デフォルト設定で続行します。")
        return None

    print("\n=== マイク選択 ===")
    for d in devices:
        print(f"[{d['index']}] {d['name']}")
    print("==================")

    while True:
        choice = input("使用するマイクの番号を入力してください (Enterでデフォルト): ").strip()
        if not choice:
            print("デフォルトマイクを使用します。")
            return None
        
        try:
            idx = int(choice)
            selected = next((d for d in devices if d['index'] == idx), None)
            if selected:
                print(f"選択されたマイク: [{selected['index']}] {selected['name']}")
                return idx
            print("無効な番号です。リストにある番号を入力してください。")
        except ValueError:
            print("数値を入力してください。")


def main() -> int:
    # Select microphone before starting GUI
    device_index = select_microphone()

    print("\n設定完了。アプリケーションを起動します。")
    print("右Altキーを押して録音を開始できます。\n")

    app = QApplication(sys.argv)

    overlay = TransparentOverlay()
    overlay.show()

    controller = STTController(device_index=device_index)

    # Show window only while recording
    def on_started():
        overlay.show_recording_state()

    def on_stopped():
        overlay.hide_recording_state()

    controller.sig_recording_started.connect(on_started)
    controller.sig_recording_stopped.connect(on_stopped)
    controller.sig_level_changed.connect(overlay.update_level)

    controller.start()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
