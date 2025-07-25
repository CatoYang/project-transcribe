# config.py

from pathlib import Path

class LowPass:
    SAMPLE_RATE = 16000
    CHANNELS = 1
    LOW_PASS_HZ = 4000  # Apply low-pass filter at 4kHz

class NormalAudio:
    SAMPLE_RATE = 16000
    CHANNELS = 1
    AUDIO_CODEC = "pcm_s16le"  


# Optional paths or directories (if needed globally)
ROOT_DIR = Path(__file__).resolve().parent
INPUT_DIR = ROOT_DIR / "data"
TEMP_DIR = ROOT_DIR / "intermediate"
finalpath = 'D:\Completed Transcriptions'

# Settings for models




if __name__ == "__main__":
    print("This is a config file. Not meant to be run directly.")