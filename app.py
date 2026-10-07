"""Gradio web demo for BirdBuddy - light, airy, offline-first.

Inline CSS and inline SVG only: no external fonts, scripts or images.
"""
import html

import gradio as gr
from src.inference import predict
from src.voice import speak

CUSTOM_CSS = """
:root {
  --sky-1: #eaf4ff;
  --sky-2: #7cc4ff;
  --sky-3: #4a9eff;
  --sky-deep: #1f6fd6;
  --cloud: #ffffff;
  --cloud-soft: #f4faff;
  --mint: #7ee8c8;
  --sand: #ffd89b;
  --ink: #1c2b3a;
  --ink-soft: #4a5f73;
  --edge: rgba(255, 255, 255, 0.9);
  --shadow: 0 20px 44px -22px rgba(31, 111, 214, 0.15);
  --shadow-lift: 0 28px 52px -22px rgba(31, 111, 214, 0.28);
}

/* ---------- Page + forced light Gradio tokens ---------- */
.gradio-container {
  color-scheme: light;
  --body-background-fill: transparent !important;
  --background-fill-primary: rgba(255, 255, 255, 0.7) !important;
  --background-fill-secondary: rgba(244, 250, 255, 0.8) !important;
  --block-background-fill: rgba(255, 255, 255, 0.7) !important;
  --block-border-color: rgba(255, 255, 255, 0.9) !important;
  --block-label-background-fill: rgba(255, 255, 255, 0.9) !important;
  --block-label-text-color: #4a5f73 !important;
  --block-title-text-color: #1c2b3a !important;
  --body-text-color: #1c2b3a !important;
  --body-text-color-subdued: #4a5f73 !important;
  --input-background-fill: rgba(244, 250, 255, 0.9) !important;
  --border-color-primary: rgba(74, 158, 255, 0.22) !important;
  --color-accent: #4a9eff !important;
  --button-secondary-background-fill: #ffffff !important;
  --button-secondary-text-color: #1c2b3a !important;
  --button-secondary-border-color: rgba(74, 158, 255, 0.3) !important;
  --panel-background-fill: transparent !important;
  --slider-color: #4a9eff !important;

  background: linear-gradient(180deg, #eaf4ff 0%, #f4faff 55%, #ffffff 100%) !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
  color: var(--ink) !important;
  min-height: 100vh;
}
.gradio-container .main { position: relative; z-index: 1; }

/* Floating blurred clouds behind everything */
.gradio-container::before,
.gradio-container::after {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}
.gradio-container::before {
  background:
    radial-gradient(440px 190px at 10% 12%, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0) 70%),
    radial-gradient(540px 220px at 90% 28%, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0) 70%);
  filter: blur(14px);
  animation: bb-drift-a 32s ease-in-out infinite alternate;
}
.gradio-container::after {
  background:
    radial-gradient(620px 240px at 28% 84%, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0) 70%),
    radial-gradient(360px 160px at 78% 78%, rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0) 70%);
  filter: blur(18px);
  animation: bb-drift-b 40s ease-in-out infinite alternate;
}
@keyframes bb-drift-a { to { transform: translateX(46px); } }
@keyframes bb-drift-b { to { transform: translateX(-52px); } }

/* Kill Gradio prose wrappers around our HTML blocks */
.bb-plain,
.bb-plain.prose,
.bb-plain > .prose,
.bb-plain > div.prose {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;
  max-width: none !important;
}

/* ---------- Hero ---------- */
.bb-hero {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  align-items: center;
  gap: 12px;
  max-width: 1100px;
  margin: 0 auto;
  padding: 34px 8px 6px;
}
.bb-eyebrow {
  display: inline-flex; align-items: center; gap: 10px;
  padding: 7px 16px;
  border-radius: 999px;
  border: 1px solid var(--edge);
  background: rgba(255, 255, 255, 0.85);
  box-shadow: var(--shadow);
  color: var(--sky-deep);
  font-size: 0.78rem; font-weight: 700;
  letter-spacing: 0.14em; text-transform: uppercase;
}
.bb-dot {
  width: 9px; height: 9px; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #ffffff, var(--mint) 55%, #2fbf9a);
}
.gradio-container .bb-title,
.bb-title {
  margin: 18px 0 12px !important;
  padding: 0 0 6px !important;
  font-size: clamp(3rem, 8vw, 5.4rem) !important;
  line-height: 1 !important;
  font-weight: 800 !important;
  letter-spacing: -0.035em !important;
  background: linear-gradient(135deg, #1f6fd6 0%, #4a9eff 58%, #7cc4ff 100%) !important;
  -webkit-background-clip: text !important;
  background-clip: text !important;
  color: transparent !important;
  -webkit-text-fill-color: transparent !important;
  border: none !important;
  text-shadow: none !important;
}
.gradio-container .bb-lede,
.bb-lede {
  max-width: 36ch;
  margin: 0 0 14px;
  color: var(--ink-soft);
  font-size: 1.12rem;
  line-height: 1.55;
}

/* Tech chips */
.bb-chips {
  display: flex; flex-wrap: wrap; gap: 8px;
  max-width: 1100px; margin: 0 auto 18px;
  padding: 0 8px;
}
.bb-chips span {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 13px;
  border-radius: 999px;
  border: 1px solid rgba(74, 158, 255, 0.22);
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 8px 18px -12px rgba(31, 111, 214, 0.4);
  color: var(--sky-deep);
  font-size: 0.78rem; font-weight: 600;
  letter-spacing: 0.02em;
}
.bb-chips span::before {
  content: "";
  width: 6px; height: 6px; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #ffffff, var(--sky-3) 60%, var(--sky-deep));
}

/* Puffy glossy bird orb */
.bb-stage {
  position: relative;
  height: 310px;
  display: flex; align-items: center; justify-content: center;
}
.bb-orb {
  position: relative;
  width: 210px; height: 210px;
  border-radius: 50%;
  display: grid; place-items: center;
  background: radial-gradient(circle at 32% 26%, #ffffff 0%, #e6f4ff 13%, #a8d8ff 38%, #4a9eff 74%, #2a78e0 100%);
  box-shadow:
    inset -20px -26px 42px rgba(31, 111, 214, 0.45),
    inset 14px 16px 30px rgba(255, 255, 255, 0.85),
    0 44px 60px -26px rgba(31, 111, 214, 0.5);
  animation: bb-bob 5s ease-in-out infinite;
}
.bb-orb::before {
  content: "";
  position: absolute;
  top: 11%; left: 17%;
  width: 36%; height: 20%;
  border-radius: 50%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0));
  transform: rotate(-26deg);
  filter: blur(1px);
}
.bb-orb::after {
  content: "";
  position: absolute;
  left: 15%; right: 15%; bottom: 7%;
  height: 16%;
  border-radius: 50%;
  background: radial-gradient(closest-side, rgba(126, 232, 200, 0.6), rgba(126, 232, 200, 0));
  filter: blur(6px);
}
.bb-orb svg { position: relative; z-index: 1; filter: drop-shadow(0 8px 8px rgba(20, 70, 150, 0.35)); }
.bb-mini {
  position: absolute;
  border-radius: 50%;
  animation: bb-bob 6s ease-in-out infinite;
}
.bb-mini.m1 {
  width: 46px; height: 46px; top: 22px; right: 18%;
  background: radial-gradient(circle at 32% 28%, #ffffff 0%, #c9f7ea 22%, var(--mint) 60%, #3fc9a5 100%);
  box-shadow: inset -5px -7px 11px rgba(20, 120, 100, 0.35), 0 14px 20px -10px rgba(47, 191, 154, 0.7);
  animation-delay: -1.5s;
}
.bb-mini.m2 {
  width: 32px; height: 32px; bottom: 54px; left: 16%;
  background: radial-gradient(circle at 32% 28%, #ffffff 0%, #fff0d0 22%, var(--sand) 60%, #f0b35c 100%);
  box-shadow: inset -4px -5px 8px rgba(160, 100, 20, 0.3), 0 12px 18px -10px rgba(240, 179, 92, 0.8);
  animation-delay: -3s;
}
.bb-ground {
  position: absolute; bottom: 10px;
  width: 180px; height: 26px;
  border-radius: 50%;
  background: radial-gradient(closest-side, rgba(31, 111, 214, 0.3), rgba(31, 111, 214, 0));
  filter: blur(5px);
  animation: bb-ground 5s ease-in-out infinite;
}
@keyframes bb-bob { 50% { transform: translateY(-12px); } }
@keyframes bb-ground { 50% { transform: scale(0.82); opacity: 0.65; } }

/* ---------- Tabs ---------- */
.bb-tabs {
  max-width: 1100px !important;
  margin: 0 auto !important;
}
.bb-tabs .tab-nav,
.bb-tabs > div > .tab-nav {
  border-bottom: 1px solid rgba(74, 158, 255, 0.18) !important;
  gap: 8px !important;
  padding: 6px 4px !important;
  background: transparent !important;
}
.bb-tabs .tab-nav button,
.bb-tabs > div > .tab-nav button {
  border: none !important;
  background: transparent !important;
  color: var(--ink-soft) !important;
  font-weight: 600 !important;
  font-size: 0.98rem !important;
  padding: 10px 18px !important;
  border-radius: 12px !important;
  transition: all 0.2s ease !important;
}
.bb-tabs .tab-nav button:hover,
.bb-tabs > div > .tab-nav button:hover {
  background: rgba(255, 255, 255, 0.75) !important;
  color: var(--sky-deep) !important;
}
.bb-tabs .tab-nav button.selected,
.bb-tabs > div > .tab-nav button.selected {
  background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%) !important;
  color: var(--sky-deep) !important;
  box-shadow: 0 8px 18px -12px rgba(31, 111, 214, 0.6),
              inset 0 0 0 1px rgba(74, 158, 255, 0.25) !important;
}

/* ---------- Glass panels (flat at rest, tilt on hover) ---------- */
.bb-panel {
  padding: 22px !important;
  border-radius: 24px !important;
  background: rgba(255, 255, 255, 0.78) !important;
  border: 1px solid var(--edge) !important;
  box-shadow: var(--shadow) !important;
  -webkit-backdrop-filter: blur(12px);
  backdrop-filter: blur(12px);
  transition: transform 0.35s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.35s;
}
.bb-panel:hover {
  transform: perspective(1400px) rotateX(1.2deg) rotateY(-1.2deg) translateY(-3px);
  box-shadow: var(--shadow-lift) !important;
}
.bb-panel .block {
  background: rgba(244, 250, 255, 0.85) !important;
  border: 1px solid rgba(74, 158, 255, 0.16) !important;
  border-radius: 18px !important;
  box-shadow: none !important;
}

.gradio-container .bb-label,
.bb-label {
  display: flex; align-items: center; gap: 12px;
  margin: 0 0 14px;
  color: var(--ink);
  font-size: 1.05rem; font-weight: 700; letter-spacing: -0.01em;
}
.bb-label i {
  font-style: normal;
  display: inline-grid; place-items: center;
  width: 32px; height: 32px;
  border-radius: 50%;
  color: var(--ink); font-size: 0.78rem; font-weight: 800;
  background: radial-gradient(circle at 32% 28%, #ffffff 0%, #c3e5ff 25%, var(--sky-2) 65%, var(--sky-3) 100%);
  box-shadow: inset -3px -4px 7px rgba(31, 111, 214, 0.35), 0 8px 12px -6px rgba(31, 111, 214, 0.55);
}
.bb-label small { color: var(--ink-soft); font-weight: 500; font-size: 0.84rem; }

/* ---------- Primary button ---------- */
button.primary, .gr-button-primary {
  min-height: 54px;
  background: linear-gradient(135deg, #2f80ec 0%, #1b63c4 100%) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 16px !important;
  font-weight: 700 !important;
  font-size: 1.05rem !important;
  letter-spacing: 0.02em;
  box-shadow: 0 14px 24px -12px rgba(31, 111, 214, 0.7) !important;
  transition: transform 0.14s ease, box-shadow 0.14s ease;
}
button.primary:hover, .gr-button-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 30px -12px rgba(31, 111, 214, 0.8) !important;
}
button.primary:active, .gr-button-primary:active {
  transform: translateY(2px);
  box-shadow: 0 6px 12px -8px rgba(31, 111, 214, 0.7) !important;
}
button:focus-visible { outline: 3px solid #1f6fd6 !important; outline-offset: 3px; }

/* ---------- Results ---------- */
.bb-empty {
  display: grid; justify-items: center; gap: 10px;
  padding: 42px 16px;
  text-align: center;
  color: var(--ink-soft);
  border: 1.5px dashed rgba(74, 158, 255, 0.35);
  border-radius: 20px;
  background: rgba(244, 250, 255, 0.6);
}
.bb-empty svg { color: var(--sky-3); }
.bb-empty strong { color: var(--ink); font-size: 1.05rem; }

.bb-res { display: grid; gap: 14px; }
.bb-card {
  --c1: #d4fbef; --c2: #7ee8c8; --c3: #2fbf9a;
  display: grid;
  grid-template-columns: 46px 1fr;
  gap: 4px 16px;
  align-items: center;
  padding: 16px 18px;
  border-radius: 22px;
  border: 1px solid var(--edge);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: var(--shadow);
  transition: transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.3s;
  animation: bb-rise 0.7s cubic-bezier(0.2, 0.8, 0.2, 1) both;
  animation-delay: calc(var(--d) * 110ms);
}
.bb-card:hover {
  transform: perspective(900px) rotateX(2deg) rotateY(-2.5deg) translateY(-3px);
  box-shadow: var(--shadow-lift);
}
.bb-card.r2 { --c1: #e0f1ff; --c2: #7cc4ff; --c3: #4a9eff; }
.bb-card.r3 { --c1: #fff2d6; --c2: #ffd89b; --c3: #f0b35c; }
.bb-card.top {
  grid-template-columns: 58px 1fr;
  padding: 24px 24px;
  background: linear-gradient(135deg, rgba(255, 216, 155, 0.6) 0%, rgba(255, 255, 255, 0.92) 48%, rgba(126, 232, 200, 0.5) 100%);
  border-color: rgba(255, 255, 255, 1);
  box-shadow: 0 26px 50px -24px rgba(240, 179, 92, 0.55), 0 10px 24px -16px rgba(31, 111, 214, 0.25);
}
@keyframes bb-rise {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: none; }
}
.bb-rank {
  grid-row: span 3;
  width: 46px; height: 46px;
  border-radius: 50%;
  display: grid; place-items: center;
  font-weight: 800; font-size: 1.05rem;
  color: var(--ink);
  background: radial-gradient(circle at 32% 28%, #ffffff 0%, var(--c1) 22%, var(--c2) 60%, var(--c3) 100%);
  box-shadow:
    inset -5px -7px 11px rgba(31, 90, 120, 0.28),
    0 12px 18px -8px var(--c3);
}
.bb-card.top .bb-rank { width: 58px; height: 58px; font-size: 1.25rem; }

.bb-badge {
  justify-self: start;
  padding: 4px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(240, 179, 92, 0.55);
  color: #8a5a10;
  font-size: 0.7rem; font-weight: 800;
  letter-spacing: 0.14em; text-transform: uppercase;
}
.gradio-container .bb-name, .bb-name { margin: 0; padding: 0; font-size: 1.2rem; font-weight: 700; color: var(--ink); letter-spacing: -0.01em; border: none; }
.gradio-container .bb-card.top .bb-name, .bb-card.top .bb-name { font-size: 1.8rem; margin-top: 4px; }
.gradio-container .bb-sci, .bb-sci { margin: 0; color: var(--ink-soft); font-style: italic; font-size: 0.95rem; }
.bb-meter { display: flex; align-items: center; gap: 12px; margin-top: 6px; }
.bb-track {
  flex: 1; height: 11px; overflow: hidden;
  border-radius: 999px;
  background: rgba(74, 158, 255, 0.14);
  box-shadow: inset 0 2px 3px rgba(31, 111, 214, 0.15);
}
.bb-fill {
  height: 100%; width: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #7ee8c8, #4a9eff);
  transform: scaleX(var(--s));
  transform-origin: left;
  animation: bb-grow 1s cubic-bezier(0.2, 0.8, 0.2, 1) both;
  animation-delay: calc(var(--d) * 110ms + 200ms);
}
@keyframes bb-grow { from { transform: scaleX(0); } }
.bb-score { min-width: 4.6ch; text-align: right; font-variant-numeric: tabular-nums; font-weight: 700; color: var(--ink); }
.bb-note {
  padding: 12px 16px;
  border-radius: 16px;
  border: 1px solid rgba(240, 179, 92, 0.55);
  background: rgba(255, 216, 155, 0.35);
  color: #6b4408; font-size: 0.92rem;
}
.bb-err { border-color: rgba(214, 90, 90, 0.4); background: rgba(255, 190, 190, 0.35); color: #7a1f1f; }

/* ---------- Settings ---------- */
.bb-settings-hint {
  color: var(--ink-soft);
  font-size: 0.92rem;
  margin: -6px 0 14px;
  line-height: 1.5;
}
.bb-settings-row {
  display: flex; justify-content: space-between; align-items: baseline;
  margin: 0 0 6px;
}
.bb-settings-row small {
  color: var(--ink-soft);
  font-size: 0.82rem;
}
.bb-settings-value {
  font-variant-numeric: tabular-nums;
  font-weight: 700;
  color: var(--sky-deep);
  font-size: 0.9rem;
}

/* Style Gradio sliders + checkboxes inside our panel */
.bb-panel input[type="range"] {
  accent-color: #4a9eff;
}
.bb-panel .gr-checkbox label,
.bb-panel label.svelte-1qxcj2k {
  color: var(--ink) !important;
}

/* System info panel */
.bb-sysinfo {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
  margin-top: 6px;
}
.bb-sysinfo-item {
  display: grid;
  gap: 4px;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(244, 250, 255, 0.9);
  border: 1px solid rgba(74, 158, 255, 0.18);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9);
}
.bb-sysinfo-label {
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ink-soft);
  font-weight: 700;
}
.bb-sysinfo-value {
  font-size: 0.98rem;
  font-weight: 700;
  color: var(--ink);
}
.bb-sysinfo-value code {
  background: rgba(74, 158, 255, 0.12);
  color: var(--sky-deep);
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 0.88em;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

/* ---------- How it works ---------- */
.bb-steps {
  max-width: 1100px; margin: 22px auto 0;
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px;
}
.bb-step {
  padding: 24px;
  border-radius: 24px;
  border: 1px solid var(--edge);
  background: rgba(255, 255, 255, 0.8);
  box-shadow: var(--shadow);
  transition: transform 0.35s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.35s;
}
.bb-step:hover {
  transform: perspective(1000px) rotateX(3deg) rotateY(-4deg) translateY(-5px);
  box-shadow: var(--shadow-lift);
}
.bb-ico {
  width: 56px; height: 56px; margin-bottom: 16px;
  display: grid; place-items: center;
  border-radius: 50%;
  color: var(--sky-deep);
  background: radial-gradient(circle at 32% 28%, #ffffff 0%, #dff1ff 30%, var(--sky-2) 100%);
  box-shadow: inset -4px -6px 10px rgba(31, 111, 214, 0.25), 0 14px 20px -10px rgba(31, 111, 214, 0.55);
}
.bb-step:nth-child(2) .bb-ico { background: radial-gradient(circle at 32% 28%, #ffffff 0%, #d4fbef 30%, var(--mint) 100%); color: #12795f; box-shadow: inset -4px -6px 10px rgba(20, 120, 100, 0.25), 0 14px 20px -10px rgba(47, 191, 154, 0.7); }
.bb-step:nth-child(3) .bb-ico { background: radial-gradient(circle at 32% 28%, #ffffff 0%, #fff2d6 30%, var(--sand) 100%); color: #8a5a10; box-shadow: inset -4px -6px 10px rgba(160, 100, 20, 0.22), 0 14px 20px -10px rgba(240, 179, 92, 0.8); }
.gradio-container .bb-step h3, .bb-step h3 { margin: 0 0 6px; padding: 0; font-size: 1.1rem; font-weight: 700; color: var(--ink); border: none; }
.gradio-container .bb-step p, .bb-step p { margin: 0; color: var(--ink-soft); font-size: 0.97rem; line-height: 1.55; }

/* ---------- Footer ---------- */
.bb-foot {
  display: flex; flex-wrap: wrap; justify-content: center; gap: 10px;
  padding: 22px 0 30px;
}
.bb-foot span {
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid var(--edge);
  background: rgba(255, 255, 255, 0.85);
  box-shadow: var(--shadow);
  color: var(--ink-soft); font-size: 0.86rem; font-weight: 600;
}

/* ---------- Hide Gradio's default footer + settings gear ---------- */
.gradio-container footer,
.gradio-container .built-with,
.gradio-container .show-api,
.gradio-container .settings,
.gradio-container button.settings,
.gradio-container .icon-button-wrapper.settings,
.gradio-container [aria-label="Settings"],
.gradio-container [aria-label="settings"] {
  display: none !important;
  visibility: hidden !important;
  height: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
}

/* ---------- Responsive + motion ---------- */
@media (max-width: 860px) {
  .bb-hero { grid-template-columns: 1fr; text-align: center; justify-items: center; }
  .bb-stage { height: 270px; }
  .bb-steps { grid-template-columns: 1fr; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
"""

# ---------------------------------------------------------------------------
# Static markup (inline SVG only, no emoji, no external assets)
# ---------------------------------------------------------------------------
BIRD_SVG = (
    '<svg viewBox="0 0 64 64" width="92" height="92" aria-hidden="true">'
    '<path d="M6 42c7-2 11-7 13-13 2-9 11-15 21-12 3 1 6 3 7 6l10 3-9 5c0 12-9 23-24 23-8 0-14-4-18-12z" fill="#ffffff"/>'
    '<path d="M17 46c9 1 17-4 21-13-2 11-10 18-21 13z" fill="rgba(31,111,214,0.25)"/>'
    '<circle cx="42" cy="22" r="2.2" fill="#1c2b3a"/></svg>'
)

HERO_HTML = (
    '<section class="bb-hero">'
    '<div>'
    '<span class="bb-eyebrow"><span class="bb-dot"></span>Acoustic species identification</span>'
    '<h1 class="bb-title">BirdBuddy</h1>'
    '<p class="bb-lede">Offline bird call identifier. Hear a bird, name a bird, '
    'with nothing ever leaving your device.</p>'
    '</div>'
    '<div class="bb-stage" aria-hidden="true">'
    '<div class="bb-ground"></div>'
    '<div class="bb-mini m1"></div>'
    '<div class="bb-mini m2"></div>'
    '<div class="bb-orb">' + BIRD_SVG + '</div>'
    '</div>'
    '</section>'
)

CHIPS_HTML = (
    '<div class="bb-chips">'
    '<span>BirdNET v2.4</span>'
    '<span>6,522 species</span>'
    '<span>ONNX Runtime · CPU</span>'
    '<span>Piper TTS</span>'
    '<span>Qwen3.5-4B LoRA</span>'
    '<span>100% offline</span>'
    '</div>'
)

IN_LABEL = (
    '<div class="bb-label"><i>01</i>Capture <small>upload a clip or record live</small></div>'
)
OUT_LABEL = (
    '<div class="bb-label"><i>02</i>Identification <small>top matches ranked by confidence</small></div>'
)
DETECT_LABEL = (
    '<div class="bb-label"><i>03</i>Detection <small>how the model ranks candidates</small></div>'
)
VOICE_LABEL = (
    '<div class="bb-label"><i>04</i>Voice <small>on-device speech synthesis</small></div>'
)
SYS_LABEL = (
    '<div class="bb-label"><i>05</i>System <small>the open-source stack behind BirdBuddy</small></div>'
)

EMPTY_HTML = (
    '<div class="bb-empty">'
    '<svg viewBox="0 0 24 24" width="44" height="44" fill="none" stroke="currentColor" '
    'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M3 12h3l2-6 4 12 3-9 2 3h4"/></svg>'
    '<strong>Waiting for a call</strong>'
    '<span>Add a bird recording on the left and press Identify.</span>'
    '</div>'
)

STEPS_HTML = (
    '<div class="bb-steps">'
    '<div class="bb-step"><div class="bb-ico">'
    '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3M8 21h8"/></svg>'
    '</div><h3>Capture</h3><p>Record outdoors or drop in a clip. Three seconds of clear audio is enough.</p></div>'
    '<div class="bb-step"><div class="bb-ico">'
    '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M3 12h3l2-6 4 12 3-9 2 3h4"/></svg>'
    '</div><h3>Analyze</h3><p>An on-device model reads the spectral fingerprint of the call.</p></div>'
    '<div class="bb-step"><div class="bb-ico">'
    '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.7 2.7L16 9.5"/></svg>'
    '</div><h3>Identify</h3><p>Get ranked species with confidence, then hear the answer spoken aloud.</p></div>'
    '</div>'
)

FOOTER_HTML = (
    '<div class="bb-foot">'
    '<span>Runs 100% on-device</span><span>No internet</span>'
    '<span>No API</span><span>Open-weight models</span>'
    '</div>'
)

SYSTEM_INFO_HTML = (
    '<div class="bb-sysinfo">'
    '<div class="bb-sysinfo-item">'
    '<span class="bb-sysinfo-label">Acoustic model</span>'
    '<span class="bb-sysinfo-value">BirdNET v2.4 <code>fp32</code></span>'
    '</div>'
    '<div class="bb-sysinfo-item">'
    '<span class="bb-sysinfo-label">Species library</span>'
    '<span class="bb-sysinfo-value">6,522 birds</span>'
    '</div>'
    '<div class="bb-sysinfo-item">'
    '<span class="bb-sysinfo-label">Runtime</span>'
    '<span class="bb-sysinfo-value">ONNX Runtime · CPU EP</span>'
    '</div>'
    '<div class="bb-sysinfo-item">'
    '<span class="bb-sysinfo-label">Text-to-speech</span>'
    '<span class="bb-sysinfo-value">Piper <code>en_US-lessac-medium</code></span>'
    '</div>'
    '<div class="bb-sysinfo-item">'
    '<span class="bb-sysinfo-label">Fine-tuned expert</span>'
    '<span class="bb-sysinfo-value">Qwen3.5-4B · LoRA <code>r=16</code></span>'
    '</div>'
    '<div class="bb-sysinfo-item">'
    '<span class="bb-sysinfo-label">Network requirement</span>'
    '<span class="bb-sysinfo-value">None · runs 100% offline</span>'
    '</div>'
    '</div>'
)


# ---------------------------------------------------------------------------
# Logic
# ---------------------------------------------------------------------------
def _notice(message, error=False):
    cls = "bb-note bb-err" if error else "bb-note"
    return '<div class="' + cls + '">' + html.escape(str(message)) + "</div>"


def _results_html(results, voice_error=None):
    cards = []
    for rank, (label, score) in enumerate(results, 1):
        common = label.split("_")[-1] if "_" in label else label
        scientific = label.split("_")[0] if "_" in label else ""
        s = max(0.0, min(1.0, float(score)))
        top = " top" if rank == 1 else ""
        badge = '<span class="bb-badge">Best match</span>' if rank == 1 else ""
        sci = ""
        if scientific:
            sci = '<p class="bb-sci">' + html.escape(scientific) + "</p>"
        delay = str(rank - 1)
        cards.append(
            '<div class="bb-card r' + str(rank) + top + '" style="--d:' + delay + '">'
            '<div class="bb-rank">' + str(rank) + "</div>"
            "<div>" + badge + '<h3 class="bb-name">' + html.escape(common) + "</h3>" + sci + "</div>"
            '<div class="bb-meter"><div class="bb-track">'
            '<div class="bb-fill" style="--s:' + format(s, ".4f") + ";--d:" + delay + '"></div></div>'
            '<span class="bb-score">' + format(float(score), ".3f") + "</span></div>"
            "</div>"
        )
    extra = ""
    if voice_error is not None:
        extra = _notice("Voice error: " + str(voice_error))
    body = "".join(cards)
    return '<div class="bb-res">' + body + extra + "</div>"


def identify(audio_path, top_k=3, threshold=0.0, voice_enabled=True, voice_speed=1.0):
    if audio_path is None:
        return _notice("No audio provided. Upload or record a bird call first."), None
    try:
        results = predict(audio_path, top_k=int(top_k))
    except Exception as e:
        return _notice("Error: " + str(e), error=True), None

    # Apply the confidence threshold (never drop everything — keep at least #1)
    try:
        th = float(threshold)
    except (TypeError, ValueError):
        th = 0.0
    if th > 0.0 and results:
        filtered = [(l, s) for (l, s) in results if float(s) >= th]
        if filtered:
            results = filtered

    if not results:
        return _notice("No matches above threshold. Lower it in Settings.", error=True), None

    voice_error = None
    wav_path = None
    if voice_enabled:
        top_common = results[0][0].split("_")[-1]
        try:
            wav_path = speak("I heard a " + top_common + ".", speed=float(voice_speed))
        except TypeError:
            # Fallback if speak() doesn't support speed yet
            try:
                wav_path = speak("I heard a " + top_common + ".")
            except Exception as e:
                wav_path = None
                voice_error = e
        except Exception as e:
            wav_path = None
            voice_error = e

    return _results_html(results, voice_error), wav_path


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
with gr.Blocks(title="BirdBuddy") as demo:
    gr.HTML(HERO_HTML, elem_classes="bb-plain")
    gr.HTML(CHIPS_HTML, elem_classes="bb-plain")

    # Persistent state widgets live outside the tabs so the button callback
    # can always read them, whether or not the Settings tab is currently open.
    with gr.Row(visible=False):
        top_k_state = gr.Slider(1, 10, value=3, step=1)
        threshold_state = gr.Slider(0.0, 1.0, value=0.0, step=0.01)
        voice_enabled_state = gr.Checkbox(value=True)
        voice_speed_state = gr.Slider(0.5, 2.0, value=1.0, step=0.1)

    with gr.Tabs(elem_classes="bb-tabs"):
        with gr.Tab("Identify"):
            with gr.Row(equal_height=True):
                with gr.Column(scale=1, elem_classes=["bb-panel"]):
                    gr.HTML(IN_LABEL, elem_classes="bb-plain")
                    audio_in = gr.Audio(
                        sources=["upload", "microphone"],
                        type="filepath",
                        label="Bird call (3+ seconds)",
                        waveform_options={
                            "show_recording_waveform": True,
                            "waveform_color": "#a8d0f5",
                            "waveform_progress_color": "#4a9eff",
                        },
                    )
                    btn = gr.Button("Identify", variant="primary", size="lg")
                with gr.Column(scale=1, elem_classes=["bb-panel"]):
                    gr.HTML(OUT_LABEL, elem_classes="bb-plain")
                    out = gr.HTML(EMPTY_HTML, elem_classes="bb-plain")
                    voice_out = gr.Audio(label="Voice result", autoplay=True)

        with gr.Tab("Settings"):
            with gr.Row(equal_height=False):
                with gr.Column(scale=1, elem_classes=["bb-panel"]):
                    gr.HTML(DETECT_LABEL, elem_classes="bb-plain")
                    gr.HTML(
                        '<p class="bb-settings-hint">'
                        "Tune how many candidates appear and how confident the model "
                        "must be before a species is shown.</p>",
                        elem_classes="bb-plain",
                    )
                    top_k_slider = gr.Slider(
                        minimum=1, maximum=10, value=3, step=1,
                        label="Top-K results",
                        info="How many ranked species to display.",
                    )
                    threshold_slider = gr.Slider(
                        minimum=0.0, maximum=1.0, value=0.0, step=0.01,
                        label="Confidence threshold",
                        info="Hide matches below this probability. 0 = show all.",
                    )
                with gr.Column(scale=1, elem_classes=["bb-panel"]):
                    gr.HTML(VOICE_LABEL, elem_classes="bb-plain")
                    gr.HTML(
                        '<p class="bb-settings-hint">'
                        "Control the on-device Piper voice. Nothing is sent to a server.</p>",
                        elem_classes="bb-plain",
                    )
                    voice_toggle = gr.Checkbox(
                        value=True,
                        label="Speak the top match aloud",
                    )
                    voice_speed = gr.Slider(
                        minimum=0.5, maximum=2.0, value=1.0, step=0.1,
                        label="Voice speed",
                        info="0.5 = slower, 1.0 = natural, 2.0 = faster.",
                    )
            with gr.Row():
                with gr.Column(elem_classes=["bb-panel"]):
                    gr.HTML(SYS_LABEL, elem_classes="bb-plain")
                    gr.HTML(SYSTEM_INFO_HTML, elem_classes="bb-plain")

    # Sync the persistent hidden state with the visible sliders
    top_k_slider.change(lambda v: v, inputs=top_k_slider, outputs=top_k_state)
    threshold_slider.change(lambda v: v, inputs=threshold_slider, outputs=threshold_state)
    voice_toggle.change(lambda v: v, inputs=voice_toggle, outputs=voice_enabled_state)
    voice_speed.change(lambda v: v, inputs=voice_speed, outputs=voice_speed_state)

    btn.click(
        identify,
        inputs=[audio_in, top_k_state, threshold_state, voice_enabled_state, voice_speed_state],
        outputs=[out, voice_out],
    )

    gr.HTML(STEPS_HTML, elem_classes="bb-plain")
    gr.HTML(FOOTER_HTML, elem_classes="bb-plain")

if __name__ == "__main__":
    import os
    demo.launch(
        css=CUSTOM_CSS,
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
    )
