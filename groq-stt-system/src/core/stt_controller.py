import threading
import time
import pyperclip
import pyautogui
import audioop
from PySide6.QtCore import QObject, Signal
from utils.audio_utils import AudioRecorder
from utils.transcriber import GroqTranscriber
from pynput import keyboard

class STTController(QObject):
    sig_recording_started = Signal()
    sig_recording_stopped = Signal()
    sig_level_changed = Signal(float)

    def __init__(self, device_index: int | None = None) -> None:
        super().__init__()
        self.recorder = AudioRecorder()
        if device_index is not None:
            self.recorder.device_index = device_index
        self.transcriber = GroqTranscriber()
        self.is_recording = False
        self.recording_thread: threading.Thread | None = None
        self.listener = None

    def start(self) -> None:
        # Windows-specific event filter to target ONLY Right Alt (VK_RMENU = 165)
        # msg: Windows message code (WM_KEYDOWN, WM_KEYUP, etc.)
        # data: KBDLLHOOKSTRUCT containing vkCode
        def win32_event_filter(msg, data):
            # VK_RMENU = 165 (0xA5)
            if data.vkCode == 165:
                # Suppress Right Alt events and handle them
                if msg == 0x0104 or msg == 0x0100: # WM_SYSKEYDOWN or WM_KEYDOWN
                    self.on_press()
                elif msg == 0x0105 or msg == 0x0101: # WM_SYSKEYUP or WM_KEYUP
                    self.on_release()
                return False # Suppress the event from OS
            return True # Allow all other keys (including Left Alt)

        self.listener = keyboard.Listener(win32_event_filter=win32_event_filter)
        self.listener.start()
    def on_press(self) -> None:
        if self.is_recording:
            return
        self.is_recording = True
        self.recorder.start_recording()
        self.sig_recording_started.emit()
        self.recording_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.recording_thread.start()

    def on_release(self) -> None:
        if not self.is_recording:
            return
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join()
        audio_data = self.recorder.stop_recording()
        self.sig_recording_stopped.emit()
        if audio_data:
            # Run transcription in a separate thread to avoid blocking the listener
            threading.Thread(target=self._transcribe_and_paste, args=(audio_data,), daemon=True).start()

    def _transcribe_and_paste(self, audio_data):
        try:
            result = self.transcriber.transcribe(audio_data)
            pyperclip.copy(result)
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'v')
        except Exception as e:
            print(f"Transcription/Paste failed: {e}")

    def _record_loop(self) -> None:
        while self.is_recording:
            self.recorder.record_chunk()
            try:
                if not self.recorder.frames:
                    continue
                data = self.recorder.frames[-1]
                level = audioop.rms(data, 2) / 32768.0
                if level < 0:
                    level = 0.0
                if level > 1:
                    level = 1.0
                
                self.sig_level_changed.emit(level)
            except Exception:
                pass
            # No sleep needed: stream.read is blocking
