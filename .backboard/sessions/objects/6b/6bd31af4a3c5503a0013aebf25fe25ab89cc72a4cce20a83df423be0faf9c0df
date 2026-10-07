---
license: cc-by-nc-sa-4.0
tags:
  - audio
  - audio-classification
  - bioacoustics
  - birds
  - birdnet
  - onnx
library_name: onnx
pipeline_tag: audio-classification
---

# BirdNET v2.4 (GLOBAL 6K) - ONNX variants

ONNX builds of the **BirdNET GLOBAL 6K V2.4** bird sound classifier, optimized for
edge deployment in [BirdNET-Go](https://github.com/tphakala/birdnet-go). This repo holds
the precision/backend variants; the stock upstream TFLite model is unchanged and not
re-hosted here.

> **Powered by BirdNET (https://birdnet.cornell.edu/)**
>
> BirdNET is developed by the K. Lisa Yang Center for Conservation Bioacoustics at the
> Cornell Lab of Ornithology and Chemnitz University of Technology. These ONNX files are
> derived from the upstream BirdNET v2.4 model. Attribution to BirdNET is a hard license
> requirement: do not strip it.

## Model summary

- **Classes:** 6,522 species (scientific + common name, see `labels.txt`)
- **Sample rate:** 48 kHz
- **Clip length:** 3 s (raw PCM waveform)
- **Input tensor:** `input`, `float32`, shape `[batch, 144000]` (3 s x 48 kHz)
- **Output tensor:** `output`, `float32`, shape `[batch, 6522]` (per-class logits; apply
  sigmoid for confidence scores in `[0, 1]`)

The two variants share an identical input/output interface, so they are drop-in
replacements for one another.

## Variants

| File | Precision | Size | Backend / target | Notes |
| --- | --- | --- | --- | --- |
| `BirdNET_v2.4_int8_arm.onnx` | INT8 (MatMul-only) + FP32 conv | ~47 MB | ONNX Runtime on ARM / low-RAM CPU | Dynamic INT8 applied only to the 1024x6522 classification head; the CNN backbone stays FP32. ~98% top-1 agreement vs FP32. The recommended low-RAM CPU build. |
| `BirdNET_v2.4_fp32.onnx` | FP32 | ~62 MB | OpenVINO (and full-precision reference) | Canonical full-precision master. Under OpenVINO it runs at f16 or f32 via `INFERENCE_PRECISION_HINT`. |

### Precision notes

- **CPU / ARM:** use `int8_arm`. Full all-ops INT8 (ConvInteger) is *not* shipped: it
  breaks accuracy (~34% top-1) and has no fast ARM kernel. Only MatMul-only quantization
  of the head is accuracy-safe.
- **OpenVINO:** use `fp32`. The empty `INFERENCE_PRECISION_HINT` resolves to f16 on
  fp16-capable hardware (A76 NEON, AVX512-FP16) and to f32 elsewhere. **Force
  `INFERENCE_PRECISION_HINT=FP32` on GPU**, where f16 miscompiles.
- f16 is intentionally not provided as a separate file: OpenVINO derives it from the FP32
  master via the precision hint, and on CPU f16 uses *more* RAM than fp32 (the runtime
  up-converts f16 weights to f32 at load).

> Note: this is the **bird classifier**. The BirdNET v2.4 backbone is also used as an
> embedding extractor for bat detection; that embedding model lives separately at
> [`tphakala/BattyBirdNET-onnx`](https://huggingface.co/tphakala/BattyBirdNET-onnx) and
> must stay FP32 (its raw embedding output overflows at f16).

## Labels

`labels.txt` has 6,522 lines, one per class, in BirdNET order. Format is
`Scientific name_Common name`, for example:

```
Abroscopus albogularis_Rufous-faced Warbler
```

Output index `i` corresponds to line `i` of `labels.txt`.

## Usage (ONNX Runtime, Python)

```python
import numpy as np, onnxruntime as ort

sess = ort.InferenceSession("BirdNET_v2.4_int8_arm.onnx")

# 3 s of 48 kHz mono PCM as float32, shape [1, 144000]
audio = np.zeros((1, 144000), dtype=np.float32)

logits = sess.run(["output"], {"input": audio})[0]   # [1, 6522]
conf = 1.0 / (1.0 + np.exp(-logits))                  # sigmoid -> [0, 1]
labels = open("labels.txt").read().splitlines()
top = conf[0].argmax()
print(labels[top], float(conf[0, top]))
```

## Checksums

See `SHA256SUMS`.

## License

BirdNET v2.4 is distributed under **CC BY-NC-SA 4.0** (non-commercial, share-alike,
attribution required). See `LICENSE` and keep the BirdNET attribution above with any use
or redistribution.

## Source

- Upstream: [birdnet-team/BirdNET-Analyzer](https://github.com/birdnet-team/BirdNET-Analyzer)
- ONNX conversion + quantization recipes: [tphakala/birdnet-go](https://github.com/tphakala/birdnet-go)
