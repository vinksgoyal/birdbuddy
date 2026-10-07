# Agent Review

BirdBuddy is a local Gradio web demo for identifying bird calls from uploaded or recorded audio. It uses an ONNX BirdNET model and label file stored under `models/birdnet`, with dependencies for audio loading, inference, and UI listed in `requirements.txt`.

The inference pipeline in `src/inference.py` lazily loads and caches the ONNX Runtime session plus labels. Audio is loaded with librosa as mono 48 kHz, then center-cropped or zero-padded to exactly 144,000 samples (3 seconds). The model input tensor is shaped as one batch of samples, logits are produced by ONNX Runtime, SciPy softmax converts them to probabilities, and the top-k label/probability pairs are returned. `app.py` wraps this in `identify()`, catches exceptions, and formats the top three matches as Markdown.

Bugs or missing error handling noticed:
- `predict()` assumes every top index has a matching label; a model/labels mismatch can raise `IndexError`.
- `top_k` is not validated, so zero, negative, or oversized values are not handled explicitly.
- All UI errors are returned as raw exception text, which is useful for debugging but unfriendly and may expose local paths.
- Audio load failures and unsupported/empty files are not handled separately from model failures.

Concrete improvements:
1. Validate `top_k`, audio path existence, and label count before returning predictions.
2. Add focused tests for cropping, padding, missing model/labels, and label/model output mismatch.
3. Replace raw UI exception messages with user-friendly errors while logging detailed diagnostics for developers.
