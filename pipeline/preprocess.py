# pipleline/preprocess_audio.py

from pathlib import Path
import subprocess

ROOT_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "staging"


SAMPLE_RATE = 16000
CHANNELS = 1
AUDIO_CODEC = "pcm_s16le"

def extract_audio(video_path: Path, output_path: Path):
    print(f"🎞️  Extracting from: {video_path.name}")
    command = [
        "ffmpeg", "-i", str(video_path),
        "-ac", str(CHANNELS),
        "-ar", str(SAMPLE_RATE),
        "-vn",
        "-acodec", AUDIO_CODEC,
        str(output_path)
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Saved to: {output_path.name}")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to extract audio from: {video_path.name}")

def process_all():
    print(f"📁 Scanning: {INPUT_DIR.resolve()}")
    for video_file in INPUT_DIR.glob("*"):
        print(f"🎞️ Found video: {video_file.name}")
        if video_file.suffix.lower() not in [".mp4", ".mkv", ".mov", ".avi"]:
            continue
        output_wav = OUTPUT_DIR / (video_file.stem + ".wav")
        if output_wav.exists():
            print(f"⏭️  Skipping (already exists): {output_wav.name}")
            continue
        extract_audio(video_file, output_wav)

if __name__ == "__main__":
    print("🚀 Running preprocess script...")
    process_all()
