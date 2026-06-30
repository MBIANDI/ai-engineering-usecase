"""
utils/agent.py
──────────────
Factory function for the LangChain pandas dataframe agent.
The agent is cached by Streamlit so it is only re-instantiated
when the dataframe content, API key, or model selection changes.

Note: AgentType enum was removed in langchain >= 0.2.
      We pass the agent type as a plain string "openai-tools" instead.
"""

from io import StringIO
import pandas as pd
import streamlit as st

from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI


@st.cache_resource(show_spinner=False)
def get_agent(df_json: str, api_key: str, model: str):
    """
    Build (or retrieve from cache) a LangChain pandas agent.

    Parameters
    ----------
    df_json  : str   JSON-serialised DataFrame (orient="split").
    api_key  : str   OpenAI API key.
    model    : str   Model identifier, e.g. "gpt-4o-mini".

    Returns
    -------
    AgentExecutor
    """
    df = pd.read_json(StringIO(df_json), orient="split")

    llm = ChatOpenAI(
        model=model,
        temperature=0,
        api_key=api_key,
    )

    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=False,
        agent_type="openai-tools",   # replaces deprecated AgentType.OPENAI_FUNCTIONS
        allow_dangerous_code=True,
        handle_parsing_errors=True,
    )
    return agent


def run_agent(agent, user_input: str, df: pd.DataFrame) -> str:
    """
    Run the agent with an enriched prompt that includes dataset context.

    Parameters
    ----------
    agent      : AgentExecutor   The cached pandas agent.
    user_input : str             Raw question from the user.
    df         : pd.DataFrame    The loaded dataset (for context metadata).

    Returns
    -------
    str   The agent's answer, or an error message.
    """
    enriched = (
        "Tu es un expert data analyst. Réponds en français de façon claire et structurée.\n"
        f"Le dataset contient {df.shape[0]} lignes et {df.shape[1]} colonnes : "
        f"{', '.join(df.columns.tolist())}.\n\n"
        f"Question : {user_input}"
    )
    try:
        result = agent.invoke({"input": enriched})
        return result.get("output", str(result))
    except Exception as exc:
        return f"❌ Erreur lors de l'analyse : {exc}"