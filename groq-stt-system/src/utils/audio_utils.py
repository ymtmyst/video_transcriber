import pyaudio
import wave
import io
from config import config

class AudioRecorder:
    """
    PyAudioを使用してマイク入力を録音するクラス。
    WAV形式でデータを保持します。
    """
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.device_index = None

    @staticmethod
    def list_audio_devices():
        """
        利用可能なマイクデバイスのリストを返します。
        Returns:
            list: [{'index': int, 'name': str}, ...]
        """
        p = pyaudio.PyAudio()
        devices = []
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                devices.append({
                    "index": i,
                    "name": p.get_device_info_by_host_api_device_index(0, i).get('name')
                })
        p.terminate()
        return devices

    def start_recording(self):
        """
        録音を開始します。
        すでに録音中の場合は無視します。
        """
        if self.is_recording:
            return
        
        self.is_recording = True
        self.frames = []
        
        # マイク入力ストリームを開く
        self.stream = self.audio.open(
            format=config.FORMAT,
            channels=config.CHANNELS,
            rate=config.SAMPLE_RATE,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=config.CHUNK_SIZE
        )
        print("Recording started... (録音開始)")

    def record_chunk(self):
        """
        音声データのチャンクを読み取り、バッファに追加します。
        このメソッドは録音ループ内で継続的に呼び出す必要があります。
        """
        if self.is_recording and self.stream:
            data = self.stream.read(config.CHUNK_SIZE)
            self.frames.append(data)

    def stop_recording(self):
        """
        録音を停止し、録音データを返します。
        
        Returns:
            io.BytesIO: WAVまたはPCMデータを格納したバイトバッファ。
            録音していない場合はNoneを返します。
        """
        if not self.is_recording:
            return None
        
        self.is_recording = False
        print("Recording stopped. (録音停止)")
        
        # ストリームの停止とクローズ
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
        return self._save_to_buffer()

    def _save_to_buffer(self):
        """
        内部バッファの音声データをWAV形式でBytesIOに書き込みます。
        """
        byte_io = io.BytesIO()
        with wave.open(byte_io, 'wb') as wf:
            wf.setnchannels(config.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(config.FORMAT))
            wf.setframerate(config.SAMPLE_RATE)
            wf.writeframes(b''.join(self.frames))
        
        byte_io.seek(0)
        return byte_io

    def __del__(self):
        self.audio.terminate()
