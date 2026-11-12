import re
import time

import streamlit as st

from src.pipeline.pipeline import run_research_system

st.set_page_config(page_title="Research Agent", page_icon="🔬", layout="wide")

# ---------- styles ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stMarkdown, .stTextInput input, button { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 2.5rem; max-width: 1100px; }
#MainMenu, footer, header [data-testid="stToolbar"] { visibility: hidden; }

.hero { text-align: center; margin-bottom: 2rem; }
.hero .badge {
    display: inline-block; padding: 4px 14px; border-radius: 999px; font-size: 12px; font-weight: 600;
    letter-spacing: .08em; text-transform: uppercase; color: #a5b4fc;
    background: rgba(99,102,241,.12); border: 1px solid rgba(99,102,241,.35);
}
.hero h1 {
    font-size: 3rem; font-weight: 800; line-height: 1.1; margin: .8rem 0 .5rem;
    background: linear-gradient(90deg, #818cf8, #c084fc 50%, #f472b6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero p { color: #94a3b8; font-size: 1.05rem; margin: 0; }

.stTextInput input {
    border-radius: 14px !important; padding: 14px 18px !important; font-size: 1rem !important;
    border: 1px solid #334155 !important; background: #0f172a !important;
}
.stTextInput input:focus { border-color: #818cf8 !important; box-shadow: 0 0 0 3px rgba(129,140,248,.25) !important; }

div.stButton > button[kind="primary"], div.stFormSubmitButton > button {
    border-radius: 14px; padding: 12px 0; font-weight: 600; border: none; width: 100%;
    background: linear-gradient(90deg, #6366f1, #a855f7); color: white; transition: transform .15s, box-shadow .15s;
}
div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button:hover {
    transform: translateY(-1px); box-shadow: 0 8px 24px rgba(139,92,246,.35); color: white;
}
div.stButton > button[kind="secondary"] {
    border-radius: 999px; font-size: 13px; border: 1px solid #334155; background: transparent; color: #cbd5e1;
}
div.stButton > button[kind="secondary"]:hover { border-color: #818cf8; color: #e0e7ff; }

.steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 1.5rem 0; }
.step {
    border-radius: 16px; padding: 16px; border: 1px solid #1e293b; background: #0f172a;
    transition: all .3s;
}
.step .icon { font-size: 22px; }
.step .name { font-weight: 600; color: #e2e8f0; margin-top: 6px; }
.step .desc { font-size: 12.5px; color: #64748b; margin-top: 2px; }
.step .status { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; margin-top: 10px; color: #475569; }
.step.running { border-color: #818cf8; box-shadow: 0 0 0 1px #818cf8, 0 0 24px rgba(129,140,248,.25); }
.step.running .status { color: #a5b4fc; }
.step.running .status::before { content: "● "; animation: pulse 1s infinite; }
.step.done { border-color: rgba(52,211,153,.4); background: rgba(16,185,129,.06); }
.step.done .status { color: #34d399; }
@keyframes pulse { 50% { opacity: .2; } }
@media (max-width: 760px) { .steps { grid-template-columns: repeat(2, 1fr); } .hero h1 { font-size: 2.2rem; } }

.score-card {
    display: flex; align-items: center; gap: 20px; padding: 20px 24px; border-radius: 16px;
    background: linear-gradient(135deg, rgba(99,102,241,.12), rgba(168,85,247,.08));
    border: 1px solid rgba(129,140,248,.3); margin-bottom: 1.2rem;
}
.score-card .num { font-size: 2.6rem; font-weight: 800; color: #e0e7ff; line-height: 1; }
.score-card .num span { font-size: 1.1rem; color: #64748b; font-weight: 600; }
.score-card .label { color: #94a3b8; font-size: 13px; }
.score-bar { height: 8px; border-radius: 99px; background: #1e293b; overflow: hidden; margin-top: 8px; width: 220px; }
.score-bar div { height: 100%; background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899); }

.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] { border-radius: 10px 10px 0 0; padding: 8px 18px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ---------- pipeline steps ----------
STEPS = [
    ("search", "🔎", "Search", "Finds sources on the web"),
    ("scrape", "📄", "Read", "Extracts key findings"),
    ("report", "✍️", "Write", "Drafts the report"),
    ("critique", "🧐", "Review", "Scores and critiques"),
]


def render_steps(placeholder, statuses):
    cards = ""
    for key, icon, name, desc in STEPS:
        s = statuses.get(key, "waiting")
        label = {"waiting": "Waiting", "running": "Working", "done": "Done"}[s]
        cards += (f'<div class="step {s}"><div class="icon">{icon}</div><div class="name">{name}</div>'
                  f'<div class="desc">{desc}</div><div class="status">{label}</div></div>')
    placeholder.markdown(f'<div class="steps">{cards}</div>', unsafe_allow_html=True)


def extract_score(critique):
    m = re.search(r"Score\W*\s*(\d+(?:\.\d+)?)", critique, re.IGNORECASE)
    return min(float(m.group(1)), 10.0) if m else None


# ---------- header ----------
st.markdown("""
<div class="hero">
  <div class="badge">Multi-agent research</div>
  <h1>Research anything, in minutes</h1>
  <p>Four AI agents search the web, read the best source, write a report, and critique it.</p>
</div>
""", unsafe_allow_html=True)

if "topic" not in st.session_state:
    st.session_state.topic = ""

with st.form("research_form", border=False):
    c1, c2 = st.columns([5, 1])
    topic = c1.text_input("Topic", key="topic", label_visibility="collapsed",
                          placeholder="e.g. The impact of artificial intelligence on healthcare")
    submitted = c2.form_submit_button("Research →")

examples = ["AI in healthcare", "Future of solid-state batteries", "Remote work and productivity"]
ex_cols = st.columns(len(examples) + 2)
for col, ex in zip(ex_cols[1:], examples):
    col.button(ex, type="secondary", use_container_width=True,
               on_click=lambda ex=ex: st.session_state.update(topic=ex))

steps_box = st.empty()

# ---------- run ----------
if submitted:
    if not topic.strip():
        st.warning("Enter a topic to research.")
    else:
        statuses = {"search": "running"}
        render_steps(steps_box, statuses)
        order = [s[0] for s in STEPS]

        def on_step(step, _data):
            statuses[step] = "done"
            i = order.index(step)
            if i + 1 < len(order):
                statuses[order[i + 1]] = "running"
            render_steps(steps_box, statuses)

        start = time.time()
        try:
            state = run_research_system(topic.strip(), on_step=on_step)
            st.session_state.result = {"topic": topic.strip(), "state": state, "secs": time.time() - start}
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.session_state.pop("result", None)

# ---------- results ----------
result = st.session_state.get("result")
if result:
    if not submitted:
        render_steps(steps_box, {k: "done" for k, *_ in STEPS})
    state = result["state"]

    st.success(f"Research on **{result['topic']}** finished in {result['secs']:.0f}s")

    tab_report, tab_critique, tab_raw = st.tabs(["📑 Report", "🧐 Critique", "🗂 Research data"])

    with tab_report:
        st.download_button("⬇ Download report (.md)", state["report"],
                           file_name=f"{result['topic'][:40].replace(' ', '_')}_report.md", mime="text/markdown")
        with st.container(border=True):
            st.markdown(state["report"])

    with tab_critique:
        score = extract_score(state["critique"])
        if score is not None:
            st.markdown(f"""
            <div class="score-card">
              <div class="num">{score:g}<span>/10</span></div>
              <div><div class="label">Critic's quality score</div>
              <div class="score-bar"><div style="width:{score * 10}%"></div></div></div>
            </div>""", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(state["critique"])

    with tab_raw:
        with st.expander("🔎 Search results", expanded=True):
            st.markdown(state["search_results"])
        with st.expander("📄 Extracted findings"):
            st.markdown(state["scraped_content"])
elif not submitted:
    render_steps(steps_box, {})
