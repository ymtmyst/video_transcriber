from groq import Groq
from config import config

class GroqTranscriber:
    """
    Groq APIを使用して音声をテキストに変換するクラス。
    """
    def __init__(self):
        self.client = Groq()

    def transcribe(self, audio_buffer):
        """
        音声データをGroq APIに送信し、文字起こし結果を取得します。
        
        Args:
            audio_buffer (io.BytesIO): WAV音声データを含むバッファ
            
        Returns:
            str: 文字起こしされたテキスト
        """
        print("Transcribing... (文字起こし中)")
        try:
            transcription = self.client.audio.transcriptions.create(
                file=("audio.wav", audio_buffer.read()),
                model=config.GROQ_MODEL,
                temperature=0.0,
                response_format="verbose_json",
                language=config.LANGUAGE
            )
            print("Transcription result: ", transcription.text, "（文字起こし完了）")

            return transcription.text
        except Exception as e:
            return f"Error during transcription: {str(e)}"
