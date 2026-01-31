import pyaudio

# Audio Configuration (音声設定)
SAMPLE_RATE = 44100
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK_SIZE = 1024

# Groq Configuration (Groq設定)
GROQ_MODEL = "whisper-large-v3-turbo"
LANGUAGE = "ja"  # Japanese (日本語)
