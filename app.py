import time
import streamlit as st
import numpy as np
import pickle
from PIL import Image

st.set_page_config(page_title="CAT vs DOG", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Share+Tech+Mono&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
    --bg: #05070d;
    --bg2: #0b0f1c;
    --cyan: #00f0ff;
    --magenta: #ff2fb2;
    --ink: #d9f4ff;
    --muted: #5c7a95;
    --card: #0c1120;
    --border: #1a2740;
}

html, body, [class*="css"] { font-family: 'Share Tech Mono', monospace; }

.stApp {
    background:
        linear-gradient(var(--bg2) 1px, transparent 1px) 0 0 / 100% 42px,
        linear-gradient(90deg, var(--bg2) 1px, transparent 1px) 0 0 / 42px 100%,
        var(--bg);
    background-blend-mode: screen, screen, normal;
    color: var(--ink);
}

/* scanline overlay */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 9999;
    background: repeating-linear-gradient(
        0deg,
        rgba(0, 240, 255, 0.025) 0px,
        rgba(0, 240, 255, 0.025) 1px,
        transparent 1px,
        transparent 3px
    );
}

#MainMenu, header, footer { visibility: hidden; }

.hero {
    text-align: center;
    padding: 2rem 0 0.4rem 0;
}
.hero h1 {
    font-family: 'Orbitron', sans-serif;
    font-weight: 800;
    font-size: 2.4rem;
    color: var(--cyan);
    text-shadow:
        0 0 8px rgba(0, 240, 255, 0.6),
        2px 0 var(--magenta),
        -2px 0 rgba(0, 240, 255, 0.5);
    letter-spacing: 0.06em;
    margin-bottom: 0.2rem;
}
.hero p {
    color: var(--muted);
    font-size: 0.8rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

[data-testid="stFileUploaderDropzone"] {
    background: var(--card);
    border: 1.5px dashed var(--border);
    border-radius: 4px;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--cyan);
    box-shadow: 0 0 16px rgba(0, 240, 255, 0.15);
}
[data-testid="stFileUploaderDropzone"] * { color: var(--muted) !important; }

.result-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.8rem 2rem;
    margin-top: 1.4rem;
    position: relative;
    box-shadow: 0 0 0 1px rgba(0, 240, 255, 0.05), 0 8px 32px rgba(0, 0, 0, 0.5);
}
.result-card::before {
    content: "";
    position: absolute;
    top: -1px; left: -1px; right: -1px; height: 2px;
    background: linear-gradient(90deg, var(--cyan), var(--magenta));
}

.verdict {
    font-family: 'Orbitron', sans-serif;
    font-weight: 800;
    font-size: 1.8rem;
    text-align: center;
    margin: 0 0 1.1rem 0;
    letter-spacing: 0.04em;
    animation: flicker-in 0.5s ease-out;
}
.verdict.cat { color: var(--magenta); text-shadow: 0 0 14px rgba(255, 47, 178, 0.6); }
.verdict.dog { color: var(--cyan); text-shadow: 0 0 14px rgba(0, 240, 255, 0.6); }

@keyframes flicker-in {
    0%   { opacity: 0; }
    20%  { opacity: 0.8; }
    30%  { opacity: 0.1; }
    45%  { opacity: 1; }
    60%  { opacity: 0.3; }
    75%  { opacity: 1; }
    100% { opacity: 1; }
}

.meter-labels {
    display: flex;
    justify-content: space-between;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-bottom: 6px;
}
.meter-track {
    position: relative;
    height: 10px;
    border-radius: 2px;
    background: linear-gradient(90deg, var(--magenta) 0%, var(--border) 48%, var(--border) 52%, var(--cyan) 100%);
    box-shadow: inset 0 0 6px rgba(0,0,0,0.6);
    overflow: visible;
}
.meter-marker {
    position: absolute;
    top: 50%;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--bg);
    border: 3px solid var(--ink);
    transform: translate(-50%, -50%);
    transition: left 0.6s cubic-bezier(.2,.9,.3,1.3);
    box-shadow: 0 0 12px rgba(217, 244, 255, 0.5);
}
.confidence-readout {
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    color: var(--muted);
    font-size: 0.8rem;
    margin-top: 0.9rem;
    letter-spacing: 0.05em;
}
.confidence-readout .num {
    color: var(--ink);
    font-weight: 700;
}

.uploaded-img {
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid var(--border);
    position: relative;
}

.terminal {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: var(--cyan);
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1rem 1.2rem;
    margin-top: 1.4rem;
    line-height: 1.7;
    min-height: 90px;
}
.terminal .line::before { content: "> "; color: var(--muted); }
.cursor {
    display: inline-block;
    width: 8px; height: 14px;
    background: var(--cyan);
    margin-left: 2px;
    animation: blink 0.9s steps(1) infinite;
    vertical-align: middle;
}
@keyframes blink { 50% { opacity: 0; } }

.footnote {
    text-align: center;
    color: var(--muted);
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    margin-top: 2.2rem;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_params(path="catdog_scratch_params.pkl"):
    with open(path, "rb") as f:
        return pickle.load(f)


def forward_propagation(X, parametres):
    activations = {'A0': X}
    C = len(parametres) // 2
    for c in range(1, C + 1):
        Z = parametres['W' + str(c)].dot(activations['A' + str(c - 1)]) + parametres['b' + str(c)]
        activations['A' + str(c)] = 1 / (1 + np.exp(-Z))
    return activations


def preprocess(image: Image.Image) -> np.ndarray:
    img = image.convert("L").resize((64, 64))
    arr = np.array(img) / 255.0
    return arr.reshape(-1, 1)



st.markdown("""
<div class="hero">
    <h1>CAT OR DOG</h1>
    <p>https://github.com/ryurina</p>
</div>
""", unsafe_allow_html=True)

try:
    parametres = load_params()
    C = len(parametres) // 2
    model_ready = True
except FileNotFoundError:
    model_ready = False
    st.warning("No trained model found. Run the training notebook first to generate `catdog_scratch_params.pkl`.")

uploaded = st.file_uploader("Drop a photo here", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded is not None and model_ready:
    image = Image.open(uploaded)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="uploaded-img">', unsafe_allow_html=True)
        st.image(image, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    #  fake  
    boot_lines = [
        "initialisation du cœur neuronal...",
        "chargement des matrices de poids...",
        "mise en mémoire tampon du tenseur d'image [64×64]...",
        "exécution de la propagation avant...",
        "décodage du verdict...",
    ]
    terminal_placeholder = col2.empty()
    shown = []
    for line in boot_lines:
        shown.append(line)
        html_lines = "".join(f'<div class="line">{l}</div>' for l in shown)
        terminal_placeholder.markdown(
            f'<div class="terminal">{html_lines}<span class="cursor"></span></div>',
            unsafe_allow_html=True,
        )
        time.sleep(0.28)

    # ---- actual inference ----
    X = preprocess(image)
    activations = forward_propagation(X, parametres)
    proba = float(activations['A' + str(C)][0, 0])  # P(dog)

    is_dog = proba >= 0.5
    label = "DOG" if is_dog else "CAT"
    emoji = "🐶" if is_dog else "🐱"
    css_class = "dog" if is_dog else "cat"
    confidence = proba if is_dog else 1 - proba
    marker_pos = proba * 100

    terminal_placeholder.markdown(f"""
    <div class="result-card">
        <div class="verdict {css_class}">{emoji} VERDICT: {label}</div>
        <div class="meter-labels">
            <span>CAT</span>
            <span>DOG</span>
        </div>
        <div class="meter-track">
            <div class="meter-marker" style="left: {marker_pos}%;"></div>
        </div>
        <div class="confidence-readout">Probabilité  <span class="num">{confidence * 100:.1f}%</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="footnote"></div>', unsafe_allow_html=True)
