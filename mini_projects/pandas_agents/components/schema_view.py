"""
components/schema_view.py
─────────────────────────
Renders the dataset overview section:
  - summary stat pills
  - column schema cards (name, type, null %)
  - raw data preview table
"""

import pandas as pd
import streamlit as st

from utils import schema_html, stats_html


def render_schema(df: pd.DataFrame) -> None:
    """
    Display the full dataset schema section.

    Parameters
    ----------
    df : pd.DataFrame   The loaded dataset.
    """
    # ── Stat pills ────────────────────────────────────────────────────────────
    st.markdown(stats_html(df), unsafe_allow_html=True)

    # ── Schema + preview side by side ─────────────────────────────────────────
    col_schema, col_preview = st.columns([1, 1], gap="large")

    with col_schema:
        st.markdown(
            '<div class="ds-section">② Schéma des colonnes</div>',
            unsafe_allow_html=True,
        )
        st.markdown(schema_html(df), unsafe_allow_html=True)

    with col_preview:
        st.markdown(
            '<div class="ds-section">Aperçu des données</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(df.head(50), use_container_width=True, height=420)