"""Local text-to-speech using Piper (open-weight TTS, runs offline)."""
import tempfile
import wave
from pathlib import Path

from piper import PiperVoice

REPO = Path(__file__).resolve().parent.parent
VOICE_PATH = REPO / "models" / "piper" / "en_US-lessac-medium.onnx"

_voice = None

def _load():
    global _voice
    if _voice is None:
        if not VOICE_PATH.exists():
            raise FileNotFoundError(f"Piper voice not found: {VOICE_PATH}")
        import onnxruntime as ort
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 1
        opts.inter_op_num_threads = 1
        opts.enable_mem_pattern = False
        opts.enable_cpu_mem_arena = False
        _voice = PiperVoice.load(str(VOICE_PATH), sess_options=opts)
    return _voice

def speak(text: str) -> str:
    """Synthesize text to a WAV file and return the path."""
    voice = _load()
    with tempfile.NamedTemporaryFile(
        suffix=".wav", delete=False, prefix="birdbuddy_"
    ) as tmp:
        path = tmp.name
    with wave.open(path, "wb") as w:
        voice.synthesize_wav(text, w)
    return path

if __name__ == "__main__":
    import sys
    path = speak(" ".join(sys.argv[1:]) or "I heard a Northern Cardinal.")
    print(path)
