"""Convert all audio under data/train/ into 3-second WAV clips."""
from pathlib import Path
import librosa
import numpy as np
import soundfile as sf

REPO = Path(__file__).resolve().parent.parent
TRAIN_DIR = REPO / "data" / "train"
OUT_DIR = REPO / "data" / "train_3s"

SAMPLE_RATE = 48000
CLIP_SAMPLES = 144000  # 3 seconds
VALID_EXT = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".opus", ".webm"}


def convert_all():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not TRAIN_DIR.exists():
        print(f"ERROR: {TRAIN_DIR} does not exist")
        return

    for class_dir in sorted(TRAIN_DIR.iterdir()):
        if not class_dir.is_dir():
            continue

        out_class = OUT_DIR / class_dir.name
        out_class.mkdir(parents=True, exist_ok=True)

        count = 0
        for audio_file in sorted(class_dir.iterdir()):
            if audio_file.suffix.lower() not in VALID_EXT:
                continue
            try:
                audio, _ = librosa.load(str(audio_file), sr=SAMPLE_RATE, mono=True)
                if len(audio) == 0:
                    print(f"    empty: {audio_file.name}")
                    continue
                if len(audio) >= CLIP_SAMPLES:
                    start = (len(audio) - CLIP_SAMPLES) // 2
                    clip = audio[start:start + CLIP_SAMPLES]
                else:
                    clip = np.pad(audio, (0, CLIP_SAMPLES - len(audio)))
                out_path = out_class / f"{audio_file.stem}_3s.wav"
                sf.write(str(out_path), clip.astype(np.float32), SAMPLE_RATE, subtype="PCM_16")
                count += 1
            except Exception as e:
                print(f"    skip {audio_file.name}: {e}")

        print(f"  {class_dir.name}: {count} clips written")


if __name__ == "__main__":
    convert_all()
    print("\n=== Summary ===")
    for class_dir in sorted(OUT_DIR.iterdir()):
        if class_dir.is_dir():
            n = len(list(class_dir.glob("*.wav")))
            print(f"  {class_dir.name}: {n} clips")
