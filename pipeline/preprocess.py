# pipeline/preprocess_audio.py

from pathlib import Path
import subprocess
import threading

ROOT_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "staging"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_audio_info(path: Path):
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=sample_rate,channels",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    if len(lines) < 2:
        return None, None
    sample_rate, channels = lines
    return int(sample_rate), int(channels)

def run_ffmpeg_with_progress(cmd, duration):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)

    def print_progress():
        for line in process.stdout:
            line = line.strip()
            if line.startswith("out_time_ms="):
                out_time_ms = int(line.split('=')[1])
                current_time = out_time_ms / 1_000_000
                if duration > 0:
                    percent = current_time / duration * 100
                    print(f"\r⏳ {int(current_time)}s / {int(duration)}s ({percent:.1f}%)", end="", flush=True)
            elif line.startswith("progress=end"):
                break

    thread = threading.Thread(target=print_progress)
    thread.start()
    process.wait()
    thread.join()

    if process.returncode != 0:
        raise RuntimeError(f"ffmpeg exited with code {process.returncode}")

def extract_audio_keep_format(video_path: Path, output_path: Path):
    sample_rate, channels = get_audio_info(video_path)
    if sample_rate is None or channels is None:
        print(f"⚠️ Could not detect audio format for {video_path.name}. Skipping.")
        return

    print(f"🎞️ Extracting audio from {video_path.name} with {sample_rate} Hz, {channels} channel(s).")

    duration_cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path)
    ]
    duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
    try:
        duration = float(duration_result.stdout.strip())
    except:
        duration = 0.0

    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", str(sample_rate),
        "-ac", str(channels),
        str(output_path),
        "-progress", "pipe:1",
        "-nostats"
    ]

    try:
        run_ffmpeg_with_progress(cmd, duration)
        print(f"\n✅ Saved to: {output_path.name}")
    except Exception as e:
        print(f"\n❌ Failed to extract audio from {video_path.name}: {e}")

def process_all():
    print(f"📁 Scanning: {INPUT_DIR.resolve()}")
    for file in INPUT_DIR.iterdir():
        if not file.is_file():
            continue
        if file.suffix.lower() not in [".mp4", ".mkv", ".mov", ".avi", ".mp3", ".wav"]:
            continue

        output_wav = OUTPUT_DIR / (file.stem + ".wav")
        if output_wav.exists():
            print(f"⏭️  Skipping (already exists): {output_wav.name}")
            continue

        extract_audio_keep_format(file, output_wav)

if __name__ == "__main__":
    print("🚀 Running audio preprocessing...")
    process_all()