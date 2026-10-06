"""Gradio web demo for BirdBuddy."""
import gradio as gr
from src.inference import predict


def identify(audio_path):
    if audio_path is None:
        return "No audio provided."
    try:
        results = predict(audio_path, top_k=3)
    except Exception as e:
        return f"Error: {e}"

    lines = ["### Top matches\n"]
    for rank, (label, score) in enumerate(results, 1):
        common = label.split("_")[-1] if "_" in label else label
        scientific = label.split("_")[0] if "_" in label else ""
        lines.append(
            f"**{rank}. {common}**  \n"
            f"*{scientific}* — confidence `{score:.3f}`\n"
        )
    return "\n".join(lines)


with gr.Blocks(title="BirdBuddy") as demo:
    gr.Markdown(
        "# BirdBuddy 🐦\n"
        "Offline bird call identifier. Runs entirely on your device — "
        "no internet, no API, no data leaves your machine."
    )
    with gr.Row():
        with gr.Column():
            audio_in = gr.Audio(
                sources=["upload", "microphone"],
                type="filepath",
                label="Bird call (3+ seconds)",
            )
            btn = gr.Button("Identify", variant="primary")
        with gr.Column():
            out = gr.Markdown("Results will appear here.")

    btn.click(identify, inputs=audio_in, outputs=out)

if __name__ == "__main__":
    demo.launch()
