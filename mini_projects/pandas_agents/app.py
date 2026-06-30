"""
app.py
──────
Entry point for the Data Science Streamlit application.

Run with:
    streamlit run app.py

Architecture
────────────
app.py                   ← orchestration only (this file)
styles/
    style.css            ← all CSS rules
    loader.py            ← injects CSS into Streamlit
utils/
    data.py              ← CSV loading + HTML helpers
    agent.py             ← LangChain pandas agent factory
components/
    sidebar.py           ← sidebar UI (API key, model, examples)
    schema_view.py       ← dataset stats + schema + preview
    chat.py              ← conversational chat interface
"""

import streamlit as st

from styles import load_css
from utils import load_csv
from components import render_sidebar, render_schema, render_chat

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Data Science · Analyse IA",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject stylesheet ─────────────────────────────────────────────────────────
load_css()

# ── Sidebar ───────────────────────────────────────────────────────────────────
api_key, model_choice = render_sidebar()

# ── Main header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="ds-header">
        <h1>◈ Data Science</h1>
        <p>Analyse statistique propulsée par IA · LangChain × Pandas Agent</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Step 1 · Upload ───────────────────────────────────────────────────────────
st.markdown('<div class="ds-section">① Chargement des données</div>', unsafe_allow_html=True)

uploaded = st.file_uploader("Déposez votre fichier CSV", type=["csv"], label_visibility="collapsed")

if uploaded is None:
    st.markdown(
        """
        <div style="text-align:center;padding:3rem;color:#8892aa;">
            <div style="font-size:2.5rem;margin-bottom:1rem">⬆</div>
            <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:600;color:#1e2535">
                Chargez un fichier CSV pour commencer
            </div>
            <div style="font-size:0.78rem;margin-top:0.5rem">
                L'agent analysera automatiquement votre dataset
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ── Step 2 · Schema ───────────────────────────────────────────────────────────
with st.spinner("Analyse du fichier…"):
    df = load_csv(uploaded.read(), uploaded.name)

render_schema(df)

st.markdown("<br>", unsafe_allow_html=True)

# ── Step 3 · Chat ─────────────────────────────────────────────────────────────
render_chat(df, api_key, model_choice)