import sys
import time
import threading
import keyboard
import pyperclip
import pyautogui
from utils.audio_utils import AudioRecorder
from utils.transcriber import GroqTranscriber

class SttApp:
    """
    Push-to-Talk形式の音声入力アプリのメインクラス。
    keyboardライブラリを使用してキーボードイベントを監視します。
    """
    def __init__(self):
        self.recorder = AudioRecorder()
        self.transcriber = GroqTranscriber()
        self.is_recording = False
        self.recording_thread = None
        
    def on_press(self, event):
        """
        キーが押されたときのコールバック。
        右Altキーが押されたら録音を開始します。
        """
        # キーのオートリピートにより連続して呼ばれるのを防ぐ
        if not self.is_recording:
            self.is_recording = True
            print("Record Start")
            self.recorder.start_recording()
            # メインスレッドがキーを監視している間、
            # 別のスレッドを開始して音声チャンクを継続的に読み取ります。
            self.recording_thread = threading.Thread(target=self._record_loop)
            self.recording_thread.start()

    def on_release(self, event):
        """
        キーが離されたときのコールバック。
        右Altキーが離されたら録音を停止し、文字起こしを実行します。
        """
        if self.is_recording:
            self.is_recording = False
            print("Record End")
            # self.is_recordingがFalseになると録音スレッドは停止します
            if self.recording_thread:
                self.recording_thread.join()
            
            audio_data = self.recorder.stop_recording()
            if audio_data:
                result = self.transcriber.transcribe(audio_data)
                print(f"\nTranscription: {result}\n")
                pyperclip.copy(result)
                time.sleep(0.1) # Wait for clipboard update and app focus restoration
                pyautogui.hotkey('ctrl', 'v')
                print("Copied and pasted.")
                print("Press Right Alt to record again... (右Altで再度録音)")

    def _record_loop(self):
        """
        録音中、マイク入力からデータを読み取り続けるためのループ処理。
        """
        while self.is_recording:
            self.recorder.record_chunk()

    def run(self):
        """
        アプリケーションのメインループを開始します。
        """
        print("Groq STT System Ready.")
        print("Hold [Right Alt] to record.")
        print("Press Ctrl+C to exit.")
        
        # キーボードフックの設定 (suppress=True でメニュー表示などのデフォルト動作をブロック)
        keyboard.on_press_key("right alt", self.on_press, suppress=True)
        keyboard.on_release_key("right alt", self.on_release, suppress=True)
        
        try:
            # メインスレッドを維持する
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nExiting...")
            # フックの解除等をここで行う場合もあるが、プロセス終了で解放される

if __name__ == "__main__":
    app = SttApp()
    app.run()
