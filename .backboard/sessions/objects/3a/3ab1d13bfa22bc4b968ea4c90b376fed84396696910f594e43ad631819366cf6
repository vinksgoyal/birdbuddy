import sys
from pathlib import Path
import onnxruntime as ort

REPO = Path(__file__).resolve().parent.parent
MODEL = REPO / "models" / "birdnet" / "model.onnx"
LABELS = REPO / "models" / "birdnet" / "labels.txt"

def main():
    if not MODEL.exists():
        print(f"FAIL: model not found at {MODEL}")
        sys.exit(1)
    if not LABELS.exists():
        print(f"FAIL: labels not found at {LABELS}")
        sys.exit(1)

    sess = ort.InferenceSession(str(MODEL), providers=["CPUExecutionProvider"])

    print("=== INPUTS ===")
    for i in sess.get_inputs():
        print(f"  name={i.name} shape={i.shape} dtype={i.type}")

    print("=== OUTPUTS ===")
    for o in sess.get_outputs():
        print(f"  name={o.name} shape={o.shape} dtype={o.type}")

    labels = LABELS.read_text(encoding="utf-8").strip().splitlines()
    print(f"=== LABELS ({len(labels)}) ===")
    print("first 5:", labels[:5])
    print("last 5:", labels[-5:])

    print("OK")

if __name__ == "__main__":
    main()
