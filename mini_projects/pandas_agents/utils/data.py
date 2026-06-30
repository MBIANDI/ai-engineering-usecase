"""
utils/data.py
─────────────
Data loading and HTML-snippet helpers used by the Streamlit views.
Keeping them here isolates all pandas logic from the UI layer.
"""

from io import StringIO
import pandas as pd
import streamlit as st


# ── CSV loading ───────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_csv(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    """
    Parse a CSV from raw bytes, auto-detecting UTF-8 / Latin-1 encoding.

    Parameters
    ----------
    file_bytes : bytes   Raw content of the uploaded file.
    file_name  : str     Original filename (used as cache key).

    Returns
    -------
    pd.DataFrame
    """
    try:
        return pd.read_csv(StringIO(file_bytes.decode("utf-8")))
    except UnicodeDecodeError:
        return pd.read_csv(StringIO(file_bytes.decode("latin-1")))


# ── dtype helpers ─────────────────────────────────────────────────────────────

def dtype_category(dtype) -> tuple[str, str]:
    """
    Map a pandas dtype to a human-readable label and a CSS class name.

    Returns
    -------
    (label, css_class) : tuple[str, str]
    """
    s = str(dtype)
    if "int" in s or "float" in s:
        return "numeric", "type-num"
    if "datetime" in s:
        return "datetime", "type-date"
    if "bool" in s:
        return "boolean", "type-bool"
    if "object" in s or "string" in s or "category" in s:
        return "text / categ.", "type-obj"
    return s, "type-other"


# ── HTML snippet builders ─────────────────────────────────────────────────────

def schema_html(df: pd.DataFrame) -> str:
    """
    Build an HTML block listing every column with its type badge
    and null-value percentage.
    """
    rows = ""
    for col in df.columns:
        label, css = dtype_category(df[col].dtype)
        null_pct = df[col].isna().mean() * 100
        null_str = (
            f"<span style='color:#8892aa;font-size:0.7rem'>"
            f"{null_pct:.0f}% null</span>"
        )
        rows += f"""
        <div class="schema-card">
            <div class="col-name">◦ {col}</div>
            {null_str}
            <span class="col-type {css}">{label}</span>
        </div>"""
    return rows


def stats_html(df: pd.DataFrame) -> str:
    """
    Build a compact stat-pill bar summarising the dataset dimensions.
    """
    n_rows, n_cols = df.shape
    n_num = df.select_dtypes("number").shape[1]
    n_cat = df.select_dtypes("object").shape[1]
    mem   = df.memory_usage(deep=True).sum() / 1024
    mem_str = f"{mem:.0f} KB" if mem < 1024 else f"{mem / 1024:.2f} MB"

    return f"""
    <div class="stats-row">
        <div class="stat-pill"><span>lignes</span><strong>{n_rows:,}</strong></div>
        <div class="stat-pill"><span>colonnes</span><strong>{n_cols}</strong></div>
        <div class="stat-pill"><span>numériques</span><strong>{n_num}</strong></div>
        <div class="stat-pill"><span>texte/catég.</span><strong>{n_cat}</strong></div>
        <div class="stat-pill"><span>mémoire</span><strong>{mem_str}</strong></div>
    </div>"""