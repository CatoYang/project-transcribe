
from pyannote.audio import Pipeline
import os
import argparse

def diarize_audio(audio_path: str, output_path: str):
    print("🔄 Loading diarization pipeline...")
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization",
                                        use_auth_token=True)

    print(f"🗣️  Running diarization on {audio_path}...")
    diarization = pipeline(audio_path)

    print(f"💾 Saving output to {output_path}...")
    with open(output_path, "w") as f:
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            f.write(f"{turn.start:.2f} --> {turn.end:.2f}: Speaker {speaker}\n")

    print("✅ Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Diarize a WAV file.")
    parser.add_argument("audio_path", help="Path to the audio file (WAV)")
    parser.add_argument("output_path", help="Path to save diarization results (TXT)")
    args = parser.parse_args()

    diarize_audio(args.audio_path, args.output_path)
