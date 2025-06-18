"""
app.py
Streamlit front-end that mimics the mobile “Advisor” chat UI.
Other modules (`nlp.py`, `data_source.py`, `charts.py`) are imported
but may be stubs until Parts 2-4 are added.
"""

import streamlit as st

# ───────────────────────── Page & CSS ──────────────────────────
st.set_page_config(page_title="Advisor", layout="centered", page_icon="💬")

MOBILE_CSS = """
<style>
/* Center the whole app inside a narrow “phone” viewport */
[data-testid="stAppViewContainer"]{
    max-width:390px;          /* iPhone 14 width */
    margin:auto;
    background:#000;          /* dark backdrop */
}
.stChatMessage{padding-bottom:12px;}
/* Tweak user / assistant bubbles */
.stChatMessage div{
    font-size:14px;
    line-height:1.45;
}
/* Rounded input pill */
.stTextInput>div>div>input{
    border:1px solid #444;
    border-radius:20px;
    padding:6px 12px;
    background:#111;
    color:#fff;
}
/* Advisor card */
.advisor-card{
    background:#0c2144;
    border-radius:12px;
    padding:16px;
    color:#fff;
    position:relative;
}
.advisor-card h4{
    margin:0 0 6px 0;
    font-size:13px;
    font-weight:600;
    opacity:.8;
}
.advisor-card p{
    margin:0 0 12px 0;
    font-size:13px;
    line-height:1.45;
}
</style>
"""
st.markdown(MOBILE_CSS, unsafe_allow_html=True)

# ──────────────────────── Session State ────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []              # [(role, msg), ...]

# ─────────────────────── CSV upload (once) ─────────────────────
if "csv_loaded" not in st.session_state:
    csv_file = st.file_uploader(
        "Upload this month’s Food-Score CSV",
        type="csv",
        accept_multiple_files=False
    )
    if csv_file is None:
        st.stop()

    # Persist bytes for later parsing by data_source.py
    import data_source as ds
    ds.store_csv(csv_file.getvalue())

    st.session_state.csv_loaded = True
    st.experimental_rerun()

# ─────────────────────── Chat history render ───────────────────
for role, message in st.session_state.history:
    st.chat_message(role).markdown(message)

# ─────────────────────── User prompt field ─────────────────────
user_prompt = st.chat_input("Write to Advisor")
if user_prompt:
    # 1. Store & echo user bubble
    st.session_state.history.append(("user", user_prompt))
    st.chat_message("user").markdown(user_prompt)

    # 2. Parse intent ➜ date range
    from nlp import parse_request, chat_with_ollama
    parsed = parse_request(user_prompt)

    if parsed:
        start_d, end_d = parsed["start"], parsed["end"]
    else:
        reply = chat_with_ollama(user_prompt)
        st.session_state.history.append(("assistant", reply))
        st.chat_message("assistant").markdown(reply)
        st.stop()

    # 3. Fetch scores
    from data_source import get_scores       # implemented in Part 2
    scores = get_scores(start_d, end_d)

    # 4. Build chart HTML
    from charts import build_chart           # implemented in Part 3
    chart_html = build_chart(scores)

    # 5. Compose insight
    if scores:
        avg = sum(scores.values()) / len(scores)
        insight = (f"Here’s a {len(scores)}-day chart of your Food Score. "
                   f"Average: **{avg:.0f}**. If you’d like deeper nutrient "
                   f"breakdowns, just ask!")
    else:
        insight = "No data found for that period."

    # 6. Save assistant message (for chat history)
    st.session_state.history.append(("assistant", insight))
    st.chat_message("assistant").markdown("")  # placeholder bubble

    # 7. Render Advisor card
    st.markdown(
        f"""
        <div class="advisor-card">
            <h4>Advisor</h4>
            <p>{insight}</p>
            {chart_html}
        </div>
        """,
        unsafe_allow_html=True
    )
