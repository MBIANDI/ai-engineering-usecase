"""
components/sidebar.py
─────────────────────
Renders the configuration sidebar and returns the user's selections.
"""

import streamlit as st


EXAMPLE_QUESTIONS = [
    "Donne-moi les statistiques descriptives",
    "Quelles sont les colonnes avec des valeurs manquantes ?",
    "Montre la distribution de [colonne]",
    "Quelle colonne a la plus forte corrélation avec [cible] ?",
    "Groupe par [col] et calcule la moyenne",
    "Y a-t-il des outliers dans les données ?",
]

AVAILABLE_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]


def render_sidebar() -> tuple[str, str]:
    """
    Render the sidebar widgets and return the user configuration.

    Returns
    -------
    api_key      : str   OpenAI API key entered by the user.
    model_choice : str   Selected model identifier.
    """
    with st.sidebar:
        st.markdown("### ◈ DataSense")
        st.markdown("---")

        # ── API key ──────────────────────────────────────────────────────────
        st.markdown("**🔑 Clé API OpenAI**")
        api_key = st.text_input(
            "OpenAI API key",
            type="password",
            placeholder="sk-...",
            label_visibility="collapsed",
            help="Votre clé API OpenAI pour alimenter l'agent",
        )

        # ── Model selector ───────────────────────────────────────────────────
        st.markdown("**🤖 Modèle**")
        model_choice = st.selectbox(
            "Modèle",
            AVAILABLE_MODELS,
            label_visibility="collapsed",
        )

        st.markdown("---")

        # ── Example questions ────────────────────────────────────────────────
        st.markdown("**📋 Exemples de questions**")
        for question in EXAMPLE_QUESTIONS:
            st.markdown(
                f"<div style='font-size:0.75rem;color:#8892aa;padding:2px 0'>"
                f"› {question}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # ── Clear conversation ───────────────────────────────────────────────
        if st.button("🗑 Effacer la conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    return api_key, model_choice