"""
styles/loader.py
────────────────
Reads the external CSS file and injects it into the Streamlit page
via st.markdown so the app keeps a clean separation between styling
and application logic.
"""

from pathlib import Path
import streamlit as st


def load_css(css_path: str | Path | None = None) -> None:
    """
    Inject the CSS file into the current Streamlit page.

    Parameters
    ----------
    css_path : str | Path | None
        Explicit path to the CSS file.  When *None* (default) the function
        looks for ``styles/style.css`` relative to this module's directory.
    """
    if css_path is None:
        css_path = Path(__file__).parent / "style.css"

    css_path = Path(css_path)

    if not css_path.exists():
        st.warning(f"⚠️ Stylesheet not found: {css_path}")
        return

    css_content = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>\n{css_content}\n</style>", unsafe_allow_html=True)