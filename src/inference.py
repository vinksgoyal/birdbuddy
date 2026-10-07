"""Bird call inference using BirdNET ONNX."""
from pathlib import Path

import librosa
import numpy as np
import onnxruntime as ort
from scipy.special import softmax

REPO = Path(__file__).resolve().parent.parent
MODEL_PATH = REPO / "models" / "birdnet" / "model.onnx"
LABELS_PATH = REPO / "models" / "birdnet" / "labels.txt"

SAMPLE_RATE = 48000
CLIP_SAMPLES = 144000  # 3 seconds @ 48kHz

_session = None
_labels = None

def _load():
    global _session, _labels
    if _session is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 1
        opts.inter_op_num_threads = 1
        opts.enable_mem_pattern = False
        opts.enable_cpu_mem_arena = False
        _session = ort.InferenceSession(
            str(MODEL_PATH), sess_options=opts, providers=["CPUExecutionProvider"]
        )
    if _labels is None:
        if not LABELS_PATH.exists():
            raise FileNotFoundError(f"Labels not found: {LABELS_PATH}")
        _labels = LABELS_PATH.read_text(encoding="utf-8").strip().splitlines()
    return _session, _labels

def _load_audio(path: str) -> np.ndarray:
    audio, _ = librosa.load(path, sr=SAMPLE_RATE, mono=True)
    if len(audio) >= CLIP_SAMPLES:
        start = (len(audio) - CLIP_SAMPLES) // 2
        audio = audio[start:start + CLIP_SAMPLES]
    else:
        pad = CLIP_SAMPLES - len(audio)
        audio = np.pad(audio, (0, pad))
    return audio.astype(np.float32).reshape(1, CLIP_SAMPLES)

def predict(audio_path: str, top_k: int = 3) -> list[tuple[str, float]]:
    session, labels = _load()
    audio = _load_audio(audio_path)
    input_name = session.get_inputs()[0].name
    logits = session.run(None, {input_name: audio})[0][0]
    probs = softmax(logits)
    idx = np.argsort(probs)[::-1][:top_k]
    return [(labels[i], float(probs[i])) for i in idx]

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m src.inference <audio_file>")
        sys.exit(1)
    results = predict(sys.argv[1])
    for rank, (label, score) in enumerate(results, 1):
        print(f"{rank}. {label}  ({score:.4f})")
