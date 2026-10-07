"""Fine-tune a small LLM with Tinker to act as a bird expert."""
import json
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

import tinker
import tinker.types as T

REPO = Path(__file__).resolve().parent.parent
TRAIN_FILE = REPO / "data" / "tinker_train.jsonl"
VAL_FILE = REPO / "data" / "tinker_val.jsonl"
OUTPUT_DIR = REPO / "data" / "tinker_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_MODEL = "Qwen/Qwen3.5-4B"
LORA_RANK = 16
EPOCHS = 3
BATCH_SIZE = 4
LR = 1e-4
CHECKPOINT_NAME = "birdbuddy-lora"


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def format_chat(example):
    text = ""
    for m in example["messages"]:
        if m["role"] == "user":
            text += f"### User: {m['content']}\n"
        else:
            text += f"### Assistant: {m['content']}\n"
    return text.strip()


def make_datum(tokenizer, text):
    tokens = tokenizer.encode(text, add_special_tokens=True)
    if len(tokens) < 2:
        return None
    model_input = T.ModelInput.from_ints(tokens[:-1])
    target_tokens = tokens[1:]
    loss_fn_inputs = {
        "target_tokens": T.TensorData(
            data=target_tokens, dtype="int64", shape=[len(target_tokens)],
        ),
        "weights": T.TensorData(
            data=[1.0] * len(target_tokens),
            dtype="float32", shape=[len(target_tokens)],
        ),
    }
    return T.Datum(model_input=model_input, loss_fn_inputs=loss_fn_inputs)


def unwrap(f):
    if hasattr(f, "result"):
        try:
            return f.result()
        except TypeError:
            return f
    return f


def extract_loss(fwd_out):
    """Pull a scalar loss out of a ForwardBackwardOutput."""
    # Try direct attribute
    val = getattr(fwd_out, "loss", None)
    if isinstance(val, (int, float)):
        return float(val)
    # Try metrics dict of lists
    metrics = getattr(fwd_out, "metrics", None)
    if isinstance(metrics, dict):
        for key in ("loss", "loss:mean", "loss:sum", "cross_entropy"):
            v = metrics.get(key)
            if v is None:
                continue
            if isinstance(v, (int, float)):
                return float(v)
            if isinstance(v, list) and v:
                flat = [x for x in v if isinstance(x, (int, float))]
                if flat:
                    return sum(flat) / len(flat)
    # Try loss_fn_outputs
    lfo = getattr(fwd_out, "loss_fn_outputs", None)
    if lfo:
        try:
            first = lfo[0] if isinstance(lfo, list) else lfo
            inner = getattr(first, "logprobs", None) or getattr(first, "loss", None)
            if isinstance(inner, (int, float)):
                return float(inner)
        except Exception:
            pass
    return None


def main():
    train_data = load_jsonl(TRAIN_FILE)
    val_data = load_jsonl(VAL_FILE)
    print(f"Loaded {len(train_data)} train / {len(val_data)} val examples")

    print("Connecting to Tinker...")
    service = tinker.ServiceClient()

    print(f"Creating LoRA training client on {BASE_MODEL} (rank={LORA_RANK})...")
    training_client = service.create_lora_training_client(
        base_model=BASE_MODEL, rank=LORA_RANK,
    )
    tokenizer = training_client.get_tokenizer()

    print("Preparing training data...")
    train_datums = [
        d for d in (make_datum(tokenizer, format_chat(ex)) for ex in train_data)
        if d is not None
    ]
    print(f"  {len(train_datums)} training datums ready")

    sample_text = format_chat({"messages": [val_data[0]["messages"][0]]})
    prompt_tokens = tokenizer.encode(sample_text, add_special_tokens=True)
    sampling_params = T.SamplingParams(max_tokens=80, temperature=0.7)

    # ---- BASELINE ----
    print("\n=== BASELINE sample (before fine-tune) ===")
    baseline_sampler = service.create_sampling_client(base_model=BASE_MODEL)
    baseline_out = unwrap(baseline_sampler.sample(
        prompt=T.ModelInput.from_ints(prompt_tokens),
        sampling_params=sampling_params,
        num_samples=1,
    ))
    baseline_text = tokenizer.decode(baseline_out.sequences[0].tokens)
    print(baseline_text)

    # ---- TRAIN ----
    print("\n=== Fine-tune ===")
    losses = []
    for epoch in range(EPOCHS):
        epoch_losses = []
        for i in range(0, len(train_datums), BATCH_SIZE):
            batch = train_datums[i : i + BATCH_SIZE]
            if not batch:
                continue
            fwd_out = unwrap(training_client.forward_backward(
                batch, loss_fn="cross_entropy"
            ))
            unwrap(training_client.optim_step(T.AdamParams(learning_rate=LR)))

            lv = extract_loss(fwd_out)
            if lv is not None:
                epoch_losses.append(lv)
            else:
                # Debug: print what we got once
                if epoch == 0 and i == 0:
                    print("  DEBUG fwd_out attrs:", [a for a in dir(fwd_out) if not a.startswith("_")])
                    print("  DEBUG metrics:", getattr(fwd_out, "metrics", None))

        if epoch_losses:
            avg = sum(epoch_losses) / len(epoch_losses)
        else:
            avg = float("nan")
        losses.append(avg)
        print(f"  epoch {epoch + 1}/{EPOCHS} — avg loss {avg:.4f} (over {len(epoch_losses)} steps)")

    print(f"Saving LoRA weights for sampler as '{CHECKPOINT_NAME}'...")
    save_out = unwrap(training_client.save_weights_for_sampler(CHECKPOINT_NAME))
    checkpoint_path = getattr(save_out, "path", None) or getattr(save_out, "model_path", None)
    if not checkpoint_path and isinstance(save_out, dict):
        checkpoint_path = save_out.get("path") or save_out.get("model_path")
    if not checkpoint_path:
        raise RuntimeError(f"Could not find checkpoint path in save output: {save_out!r}")
    print(f"Checkpoint path: {checkpoint_path}")

    # ---- FINE-TUNED ----
    print("\n=== FINE-TUNED sample (after training) ===")
    ft_sampler = service.create_sampling_client(
        base_model=BASE_MODEL,
        model_path=checkpoint_path,
    )
    ft_out = unwrap(ft_sampler.sample(
        prompt=T.ModelInput.from_ints(prompt_tokens),
        sampling_params=sampling_params,
        num_samples=1,
    ))
    ft_text = tokenizer.decode(ft_out.sequences[0].tokens)
    print(ft_text)

    log = {
        "base_model": BASE_MODEL,
        "checkpoint_name": CHECKPOINT_NAME,
        "checkpoint_path": checkpoint_path,
        "epochs": EPOCHS,
        "losses": losses,
        "baseline_sample": baseline_text,
        "finetuned_sample": ft_text,
        "prompt": sample_text,
    }
    (OUTPUT_DIR / "results.json").write_text(json.dumps(log, indent=2))
    print(f"\nResults saved to {OUTPUT_DIR / 'results.json'}")


if __name__ == "__main__":
    main()
