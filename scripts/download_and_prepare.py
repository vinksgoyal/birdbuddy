"""Download bird recordings from Xeno-canto and prepare 3-second WAV clips."""
import os
import re
import time
from pathlib import Path
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
import librosa
import numpy as np
import soundfile as sf

REPO = Path(__file__).resolve().parent.parent
TRAIN_DIR = REPO / "data" / "train"
OUT_DIR = REPO / "data" / "train_3s"

SPECIES = {
    "american_robin": "American Robin",
    "northern_cardinal": "Northern Cardinal",
    "blue_jay": "Blue Jay",
}

NOISE_URLS = [
    "https://cdn.jsdelivr.net/npm/sounds-for-focus@0.1.0/audio/rain/light-rain.mp3",
    "https://cdn.jsdelivr.net/npm/sounds-for-focus@0.1.0/audio/nature/forest.mp3",
    "https://cdn.jsdelivr.net/npm/sounds-for-focus@0.1.0/audio/nature/wind.mp3",
    "https://cdn.jsdelivr.net/npm/sounds-for-focus@0.1.0/audio/rain/heavy-rain.mp3",
    "https://cdn.jsdelivr.net/npm/sounds-for-focus@0.1.0/audio/nature/crickets.mp3",
]

SAMPLE_RATE = 48000
CLIP_SAMPLES = 144000  # 3 seconds


def download_species(species_key: str, common_name: str, max_recordings: int = 12):
    """Download up to max_recordings MP3s from Xeno-canto for a species."""
    out_dir = TRAIN_DIR / species_key
    out_dir.mkdir(parents=True, exist_ok=True)

    search_url = f"https://xeno-canto.org/explore?query={quote(common_name)}"
    headers = {"User-Agent": "Mozilla/5.0 (BirdBuddy research)"}
    resp = requests.get(search_url, headers=headers, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/download" in href:
            full = href if href.startswith("http") else f"https://xeno-canto.org{href}"
            links.append(full)

    links = list(dict.fromkeys(links))[:max_recordings]
    print(f"  Found {len(links)} download links for {common_name}")

    downloaded = 0
    for idx, url in enumerate(links, 1):
        fname = out_dir / f"{species_key}_{idx:03d}.mp3"
        if fname.exists():
            downloaded += 1
            continue
        try:
            r = requests.get(url, headers=headers, timeout=60)
            r.raise_for_status()
            fname.write_bytes(r.content)
            downloaded += 1
            time.sleep(0.8)  # be polite to Xeno-canto
        except Exception as e:
            print(f"    skip {url}: {e}")

    print(f"  Downloaded {downloaded} files for {common_name}")


def download_noise():
    """Download ambient noise samples."""
    out_dir = TRAIN_DIR / "noise"
    out_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    for idx, url in enumerate(NOISE_URLS, 1):
        fname = out_dir / f"noise_{idx:03d}.mp3"
        if fname.exists():
            downloaded += 1
            continue
        try:
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            fname.write_bytes(r.content)
            downloaded += 1
        except Exception as e:
            print(f"    noise skip {url}: {e}")

    print(f"  Downloaded {downloaded} noise files")


def convert_all():
    """Convert every audio file under data/train/ into 3-second WAV clips."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for class_dir in sorted(TRAIN_DIR.iterdir()):
        if not class_dir.is_dir():
            continue
        out_class = OUT_DIR / class_dir.name
        out_class.mkdir(parents=True, exist_ok=True)

        count = 0
        for audio_file in class_dir.iterdir():
            if audio_file.suffix.lower() not in {".mp3", ".wav", ".flac", ".ogg"}:
                continue
            try:
                audio, _ = librosa.load(str(audio_file), sr=SAMPLE_RATE, mono=True)
                if len(audio) >= CLIP_SAMPLES:
                    start = (len(audio) - CLIP_SAMPLES) // 2
                    clip = audio[start : start + CLIP_SAMPLES]
                else:
                    clip = np.pad(audio, (0, CLIP_SAMPLES - len(audio)))
                out_path = out_class / f"{audio_file.stem}_3s.wav"
                sf.write(str(out_path), clip.astype(np.float32), SAMPLE_RATE, subtype="PCM_16")
                count += 1
            except Exception as e:
                print(f"    convert skip {audio_file.name}: {e}")

        print(f"  {class_dir.name}: {count} clips written")


def main():
    TRAIN_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Step 1: Download bird recordings ===")
    for key, name in SPECIES.items():
        print(f"\n[{name}]")
        download_species(key, name)

    print("\n=== Step 2: Download noise samples ===")
    download_noise()

    print("\n=== Step 3: Convert to 3-second WAV clips ===")
    convert_all()

    print("\n=== Summary ===")
    for class_dir in sorted(OUT_DIR.iterdir()):
        if class_dir.is_dir():
            n = len(list(class_dir.glob("*.wav")))
            print(f"  {class_dir.name}: {n} clips")


if __name__ == "__main__":
    main()
