"""Streamlit front-end for the Advisor chatbot."""

import streamlit as st
from . import data_source as ds
from .charts import build_chart
from .nlp import parse_request
from .ollama_fallback import chat as chat_with_ollama
from .data_source import load_cached
from .config import CACHE_FILE

MOBILE_CSS = """
<style>
[data-testid="stAppViewContainer"]{
    max-width:390px;
    margin:auto;
    background:#000;
}
.stChatMessage{padding-bottom:12px;}
.stChatMessage div{font-size:14px;line-height:1.45;}
.stTextInput>div>div>input{
    border:1px solid #444;
    border-radius:20px;
    padding:6px 12px;
    background:#111;
    color:#fff;
}
.advisor-card{background:#0c2144;border-radius:12px;padding:16px;color:#fff;position:relative;}
.advisor-card h4{margin:0 0 6px 0;font-size:13px;font-weight:600;opacity:.8;}
.advisor-card p{margin:0 0 12px 0;font-size:13px;line-height:1.45;}
</style>
"""


def main() -> None:
    st.set_page_config(page_title="Advisor", layout="centered", page_icon="💬")
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)

    if "history" not in st.session_state:
        st.session_state.history = []

    if "csv_loaded" not in st.session_state:
        if load_cached():
            st.session_state.csv_loaded = True
            st.session_state.csv_bytes = CACHE_FILE.read_bytes()
        else:
            csv_file = st.file_uploader(
                "Upload this month’s Food-Score CSV",
                type="csv",
                accept_multiple_files=False,
            )
            if csv_file is None:
                st.stop()
            st.session_state.csv_bytes = csv_file.getvalue()
            ds.store_csv(st.session_state.csv_bytes)
            st.session_state.csv_loaded = True
            st.experimental_rerun()

    for role, message in st.session_state.history:
        st.chat_message(role).markdown(message)

    user_prompt = st.chat_input("Write to Advisor")
    if not user_prompt:
        return

    st.session_state.history.append(("user", user_prompt))
    st.chat_message("user").markdown(user_prompt)

    parsed = parse_request(user_prompt)
    if not parsed:
        reply = chat_with_ollama(user_prompt)
        st.session_state.history.append(("assistant", reply))
        st.chat_message("assistant").markdown(reply)
        return

    scores = ds.get_scores(parsed["start"], parsed["end"])
    chart_html = build_chart(scores)
    if scores:
        avg = sum(scores.values()) / len(scores)
        insight = (
            f"Here’s a {len(scores)}-day chart of your Food Score. "
            f"Average: **{avg:.0f}**. If you’d like deeper nutrient breakdowns, just ask!"
        )
    else:
        insight = "No data found for that period."

    st.session_state.history.append(("assistant", insight))
    st.chat_message("assistant").markdown("")
    st.markdown(
        f"""
        <div class='advisor-card'>
            <h4>Advisor</h4>
            <p>{insight}</p>
            {chart_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
