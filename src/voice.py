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
        _voice = PiperVoice.load(str(VOICE_PATH))
    return _voice

def speak(text: str) -> str:
    """Synthesize text to a WAV file and return the path."""
    voice = _load()
    tmp = tempfile.NamedTemporaryFile(
        suffix=".wav", delete=False, prefix="birdbuddy_"
    )
    tmp.close()
    with wave.open(tmp.name, "wb") as w:
        voice.synthesize_wav(text, w)
    return tmp.name

if __name__ == "__main__":
    import sys
    path = speak(" ".join(sys.argv[1:]) or "I heard a Northern Cardinal.")
    print(path)
