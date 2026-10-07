"""Convert source recordings into 3-second, 48 kHz mono WAV clips."""

from pathlib import Path

import librosa
import numpy as np
import soundfile as sf


SOURCE = Path("data/train")
OUTPUT = Path("data/train_3s")
SAMPLE_RATE = 48000
CLIP_SAMPLES = SAMPLE_RATE * 3
EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg"}


def prepare_file(path: Path, class_name: str) -> None:
    audio, _ = librosa.load(path, sr=SAMPLE_RATE, mono=True)
    if len(audio) >= CLIP_SAMPLES:
        start = (len(audio) - CLIP_SAMPLES) // 2
        clip = audio[start : start + CLIP_SAMPLES]
    else:
        clip = np.pad(audio, (0, CLIP_SAMPLES - len(audio)))

    destination = OUTPUT / class_name / f"{path.stem}_clip.wav"
    destination.parent.mkdir(parents=True, exist_ok=True)
    sf.write(destination, clip.astype(np.float32), SAMPLE_RATE, subtype="PCM_16")


def main() -> None:
    counts: dict[str, int] = {}
    if not SOURCE.exists():
        print(f"{SOURCE} does not exist; no files processed.")
        return

    for path in sorted(SOURCE.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        relative_parts = path.relative_to(SOURCE).parts
        class_name = relative_parts[0] if len(relative_parts) > 1 else path.parent.name
        prepare_file(path, class_name)
        counts[class_name] = counts.get(class_name, 0) + 1

    print("Summary:")
    for class_name, count in sorted(counts.items()):
        print(f"{class_name} -> {count}")


if __name__ == "__main__":
    main()
