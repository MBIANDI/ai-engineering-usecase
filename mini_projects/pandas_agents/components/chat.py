"""
components/chat.py
──────────────────
Renders the conversational chat interface:
  - message history (user + agent bubbles)
  - input form with send button
Triggers the agent and updates session state on submission.
"""

import pandas as pd
import streamlit as st

from utils import get_agent, run_agent


def _render_history() -> None:
    """Display all messages stored in session state."""
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="msg-label">Vous</div>'
                f'<div class="msg-user">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="msg-label">◈ Agent DataSense</div>'
                f'<div class="msg-ai">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )


def render_chat(df: pd.DataFrame, api_key: str, model: str) -> None:
    """
    Render the full chat section.

    Parameters
    ----------
    df      : pd.DataFrame   The loaded dataset passed to the agent.
    api_key : str            OpenAI API key.
    model   : str            Model identifier.
    """
    st.markdown(
        '<div class="ds-section">③ Interrogez vos données</div>',
        unsafe_allow_html=True,
    )

    # Guard: API key required
    if not api_key:
        st.warning("⚠️ Entrez votre clé API OpenAI dans la barre latérale pour activer l'agent.")
        return

    # Initialise session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display conversation history
    _render_history()

    # ── Input form ────────────────────────────────────────────────────────────
    with st.form("chat_form", clear_on_submit=True):
        cols = st.columns([6, 1])
        with cols[0]:
            user_input = st.text_input(
                "Question",
                placeholder="Ex : Quelles colonnes ont le plus de valeurs manquantes ?",
                label_visibility="collapsed",
            )
        with cols[1]:
            submitted = st.form_submit_button(
                "Envoyer ▶", use_container_width=True, type="primary"
            )

    # ── Handle submission ─────────────────────────────────────────────────────
    if submitted and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})

        agent = get_agent(df.to_json(orient="split"), api_key, model)

        with st.spinner("L'agent analyse vos données…"):
            answer = run_agent(agent, user_input, df)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()