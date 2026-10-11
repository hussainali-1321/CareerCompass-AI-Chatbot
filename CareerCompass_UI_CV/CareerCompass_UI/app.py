import html
import re
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
OLLAMA_BASE = "http://localhost:11434"
OLLAMA_URL = f"{OLLAMA_BASE}/api/chat"

JOBS_FILE_CANDIDATES = [
    Path("Pakistan Available Job Dec 19 - Mar-21.csv"),
    Path("../Pakistan Available Job Dec 19 - Mar-21.csv"),
    Path("../../Pakistan Available Job Dec 19 - Mar-21.csv"),
]

SKILLS = [
    "python", "java", "c++", "c#", "sql", "mysql", "mongodb",
    "machine learning", "deep learning", "data analysis",
    "data science", "pandas", "numpy", "tensorflow", "pytorch",
    "keras", "excel", "power bi", "tableau",
    "artificial intelligence", "computer vision", "nlp",
    "html", "css", "javascript", "typescript", "react",
    "node.js", "node", "django", "flask", "fastapi", "git",
    "github", "linux", "networking", "cybersecurity", "aws",
    "azure", "docker", "kubernetes", "project management",
    "communication", "wordpress", "php", "laravel", "flutter",
    "android", "figma", "testing", "selenium", "statistics",
    "problem solving", "data visualization", "rest api"
]

ROLE_TERMS = [
    "software engineer", "software developer", "python developer",
    "web developer", "frontend developer", "backend developer",
    "full stack developer", "data analyst", "data scientist",
    "machine learning engineer", "ai engineer", "ai developer",
    "database administrator", "network engineer",
    "cybersecurity analyst", "system administrator",
    "qa engineer", "software tester", "devops engineer",
    "business analyst", "it support", "technical support",
    "mobile app developer"
]

GREETING = (
    "Assalam-o-Alaikum! I'm Career Compass. Ask me about your CV, "
    "skills to learn, interview prep or career paths. "
    "Roman Urdu ya English, dono chalega."
)

SUGGESTIONS = [
    "Which skills should I learn next?",
    "How can I improve my CV?",
    "Mock interview questions for a Python developer",
    "Data Science aur Web Development mein se kya behtar hai?",
]

# ----------------------------------------------------------------------------
# Page setup + theme
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Career Compass",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

:root {
    --ink: #0F1B33;
    --ink-soft: #1B2A4A;
    --paper: #F4F6FA;
    --card: #FFFFFF;
    --line: #E1E6EF;
    --muted: #64708A;
    --blue: #2F5BEA;
    --blue-soft: #E8EEFF;
    --teal: #0E9F8E;
    --teal-soft: #DDF5F1;
    --amber: #B7791F;
    --amber-soft: #FDF1DC;
    --red: #C0392B;
}

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
}
.stApp { background: var(--paper); }

/* hide default chrome */
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1180px; }

/* ---------- hero ---------- */
.hero {
    background: var(--ink);
    border-radius: 18px;
    padding: 30px 36px;
    display: flex; align-items: center; justify-content: space-between; gap: 24px;
    margin-bottom: 22px;
    position: relative; overflow: hidden;
}
.hero::after {
    content: ""; position: absolute; right: -60px; top: -60px;
    width: 260px; height: 260px; border-radius: 50%;
    border: 2px solid rgba(255,255,255,.07);
    box-shadow: 0 0 0 36px rgba(255,255,255,.03), 0 0 0 72px rgba(255,255,255,.02);
}
.hero h1 {
    color: #fff; font-size: 2rem; font-weight: 800; letter-spacing: -.5px;
    margin: 0 0 6px 0; padding: 0;
}
.hero p { color: #AFBBD6; margin: 0; font-size: .98rem; max-width: 560px; line-height: 1.55; }
.hero-badge {
    z-index: 1; font-family: 'JetBrains Mono', monospace; font-size: .75rem;
    color: #7FE3D5; background: rgba(14,159,142,.15);
    border: 1px solid rgba(127,227,213,.35);
    padding: 6px 12px; border-radius: 999px; white-space: nowrap;
}

/* ---------- tabs ---------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px; border-bottom: 1px solid var(--line); padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    height: 46px; padding: 0 18px; border-radius: 10px 10px 0 0;
    font-weight: 600; color: var(--muted); background: transparent;
}
.stTabs [aria-selected="true"] { color: var(--blue) !important; background: var(--card); }
.stTabs [data-baseweb="tab-highlight"] { background: var(--blue) !important; height: 3px; }

/* ---------- section headings ---------- */
.sec-title { font-size: 1.15rem; font-weight: 700; color: var(--ink); margin: 6px 0 2px 0; }
.sec-sub { color: var(--muted); font-size: .9rem; margin-bottom: 14px; }

/* ---------- panels ---------- */
.panel {
    background: var(--card); border: 1px solid var(--line);
    border-radius: 14px; padding: 18px 20px; margin-bottom: 14px;
}
.panel-title { font-weight: 700; color: var(--ink); margin-bottom: 8px; }

/* ---------- stat cards ---------- */
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 14px 0; }
.stat {
    background: var(--card); border: 1px solid var(--line);
    border-radius: 14px; padding: 14px 16px;
}
.stat .v { font-size: 1.6rem; font-weight: 800; color: var(--ink); line-height: 1.1; }
.stat .l { font-size: .8rem; color: var(--muted); margin-top: 4px; }
.stat.accent { border-left: 4px solid var(--blue); }

/* ---------- chips ---------- */
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip {
    background: var(--blue-soft); color: var(--blue);
    font-size: .78rem; font-weight: 600; padding: 4px 10px; border-radius: 999px;
}
.chip.teal { background: var(--teal-soft); color: var(--teal); }
.chip.gray { background: #EEF1F6; color: var(--muted); }

/* ---------- job cards ---------- */
.job {
    background: var(--card); border: 1px solid var(--line);
    border-radius: 14px; padding: 16px 18px; margin-bottom: 12px;
    display: grid; grid-template-columns: 1fr auto; gap: 14px;
}
.job:hover { border-color: #C5D1F5; }
.job h4 { margin: 0 0 3px 0; font-size: 1.02rem; color: var(--ink); font-weight: 700; }
.job .meta { color: var(--muted); font-size: .85rem; margin-bottom: 10px; }
.job .desc { color: #3C4862; font-size: .85rem; line-height: 1.5; margin: 10px 0 0 0; }
.job a.apply {
    display: inline-block; margin-top: 10px; font-size: .83rem; font-weight: 600;
    color: var(--blue); text-decoration: none;
}
.job a.apply:hover { text-decoration: underline; }
.score {
    min-width: 74px; height: 74px; border-radius: 50%;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    font-weight: 800; font-size: 1.15rem;
}
.score small { font-weight: 600; font-size: .62rem; opacity: .8; }
.score.hi  { background: var(--teal-soft);  color: var(--teal); }
.score.mid { background: var(--blue-soft);  color: var(--blue); }
.score.lo  { background: var(--amber-soft); color: var(--amber); }

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] { background: var(--ink); }
section[data-testid="stSidebar"] * { color: #D5DDF0; }
section[data-testid="stSidebar"] input {
    background: var(--ink-soft) !important; color: #fff !important;
    border: 1px solid #2C3E66 !important; border-radius: 8px;
}
.brand { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.brand .logo {
    width: 38px; height: 38px; border-radius: 10px; background: var(--blue);
    display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
}
.brand .name { color: #fff !important; font-weight: 800; font-size: 1.1rem; }
.brand-sub { color: #8E9BBA !important; font-size: .8rem; margin-bottom: 18px; }
.side-label { color: #8E9BBA !important; font-size: .78rem; font-weight: 600; margin: 18px 0 8px 0; }
.status-row { display: flex; align-items: center; gap: 9px; font-size: .86rem; padding: 5px 0; }
.dot { width: 9px; height: 9px; border-radius: 50%; background: #4A5878; flex: none; }
.dot.ok { background: #35D0B6; box-shadow: 0 0 0 3px rgba(53,208,182,.18); }
.dot.bad { background: #E5604F; }

/* ---------- buttons ---------- */
.stButton > button, .stDownloadButton > button {
    border-radius: 10px; font-weight: 600; padding: .55rem 1.1rem;
    border: 1px solid var(--line);
}
.stButton > button[kind="primary"] {
    background: var(--blue); border-color: var(--blue); color: #fff;
}
.stButton > button[kind="primary"]:hover { background: #2349C7; border-color: #2349C7; }
.stButton > button:focus-visible { outline: 3px solid #9DB4FF; outline-offset: 2px; }

/* ---------- uploader / expander / chat ---------- */
[data-testid="stFileUploaderDropzone"] {
    background: var(--card); border: 1.5px dashed #B9C5E4; border-radius: 14px;
}
[data-testid="stExpander"] {
    background: var(--card); border: 1px solid var(--line); border-radius: 12px;
}
[data-testid="stChatMessage"] {
    background: var(--card); border: 1px solid var(--line);
    border-radius: 14px; padding: 12px 16px;
}
[data-testid="stChatInput"] { border-radius: 14px; }

.footer-note { text-align: center; color: var(--muted); font-size: .8rem; margin-top: 32px; }

@media (max-width: 760px) {
    .hero { flex-direction: column; align-items: flex-start; padding: 22px; }
    .stats { grid-template-columns: repeat(2, 1fr); }
    .job { grid-template-columns: 1fr; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------------
st.session_state.setdefault("cv_text", "")
st.session_state.setdefault("cv_name", "")
st.session_state.setdefault("cv_analysis", "")
st.session_state.setdefault("matches", None)
st.session_state.setdefault("detected_skills", [])
st.session_state.setdefault("messages", [{"role": "assistant", "content": GREETING}])


# ----------------------------------------------------------------------------
# Helpers: HTML
# ----------------------------------------------------------------------------
def esc(value):
    return html.escape(str(value))


def chips_html(items, kind=""):
    if not items:
        return '<span class="chip gray">None detected</span>'
    return '<div class="chips">' + "".join(
        f'<span class="chip {kind}">{esc(i)}</span>' for i in items
    ) + "</div>"


def section(title, subtitle=""):
    st.markdown(
        f'<div class="sec-title">{esc(title)}</div>'
        f'<div class="sec-sub">{esc(subtitle)}</div>',
        unsafe_allow_html=True,
    )


def stat_cards(items):
    cards = "".join(
        f'<div class="stat {"accent" if i == 0 else ""}">'
        f'<div class="v">{esc(v)}</div><div class="l">{esc(l)}</div></div>'
        for i, (v, l) in enumerate(items)
    )
    st.markdown(f'<div class="stats">{cards}</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Helpers: Ollama + files
# ----------------------------------------------------------------------------
def ollama_online():
    try:
        return requests.get(f"{OLLAMA_BASE}/api/tags", timeout=1.5).ok
    except Exception:
        return False


def extract_text(uploaded):
    suffix = Path(uploaded.name).suffix.lower()

    if suffix == ".txt":
        return uploaded.getvalue().decode("utf-8", errors="ignore")

    if suffix == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(uploaded)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            st.error("PDF support missing. Run: python -m pip install pypdf")
            return ""
        except Exception as exc:
            st.error(f"Could not read the PDF: {exc}")
            return ""

    if suffix == ".docx":
        try:
            from docx import Document
            doc = Document(uploaded)
            return "\n".join(p.text for p in doc.paragraphs)
        except ImportError:
            st.error("DOCX support missing. Run: python -m pip install python-docx")
            return ""
        except Exception as exc:
            st.error(f"Could not read the DOCX: {exc}")
            return ""

    st.error("Supported formats: PDF, DOCX, TXT")
    return ""


def ask_ollama(messages, model_name, num_predict=350):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model_name.strip(),
            "messages": messages,
            "stream": False,
            "options": {"num_ctx": 2048, "num_predict": num_predict},
        },
        timeout=(10, 600),
    )
    response.raise_for_status()
    return response.json().get("message", {}).get("content", "")


def load_jobs(uploaded=None):
    if uploaded is not None:
        try:
            return pd.read_csv(uploaded)
        except Exception as exc:
            st.error(f"Could not read the CSV: {exc}")
            return None

    for path in JOBS_FILE_CANDIDATES:
        if path.exists():
            try:
                return pd.read_csv(path)
            except Exception:
                continue
    return None


# ----------------------------------------------------------------------------
# Matching logic (unchanged from original)
# ----------------------------------------------------------------------------
def normalize(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def find_column(df, candidates):
    normalized = {normalize(column): column for column in df.columns}

    for candidate in candidates:
        target = normalize(candidate)
        if target in normalized:
            return normalized[target]

    for norm, original in normalized.items():
        if any(normalize(c) in norm for c in candidates):
            return original
    return None


def find_terms(text, terms):
    text = text.lower()
    found = []
    for term in terms:
        pattern = r"(?<![a-z0-9])" + re.escape(term.lower()) + r"(?![a-z0-9])"
        if re.search(pattern, text):
            found.append(term)
    return found


def recommend_jobs(df, cv_text):
    cv_skills = find_terms(cv_text, SKILLS)

    if df is None or df.empty or not cv_skills:
        return pd.DataFrame(), cv_skills

    title_col = find_column(df, ["Job Name", "Job Title", "Title", "Position", "Role"])
    company_col = find_column(df, ["Company Name", "Company", "Employer"])
    city_col = find_column(df, ["City", "Location"])
    department_col = find_column(df, ["Department", "Category", "Job Category"])
    description_col = find_column(df, ["JD", "Job Description", "Description"])
    experience_col = find_column(df, ["Experience Required", "Experience"])
    link_col = find_column(
        df, ["Apply Link", "Application Link", "Job URL", "URL", "Link"]
    )

    text_columns = [c for c in df.columns if pd.api.types.is_object_dtype(df[c])]
    if not text_columns:
        return pd.DataFrame(), cv_skills

    work = df.copy()
    work["_search"] = (
        work[text_columns].fillna("").astype(str).agg(" ".join, axis=1).str.lower()
    )
    work["_matched_skills"] = work["_search"].apply(
        lambda text: [s for s in cv_skills if s.lower() in text]
    )
    work["_skill_count"] = work["_matched_skills"].apply(len)
    work["_match_percent"] = (
        work["_skill_count"] / len(cv_skills) * 100
    ).round().astype(int)

    cv_roles = find_terms(cv_text, ROLE_TERMS)
    role_columns = [c for c in [title_col, department_col] if c]

    if role_columns and cv_roles:
        role_text = (
            work[role_columns].fillna("").astype(str).agg(" ".join, axis=1).str.lower()
        )
        role_bonus = role_text.apply(lambda t: any(r in t for r in cv_roles))
        work["_match_percent"] = (
            work["_match_percent"] + role_bonus.astype(int) * 10
        ).clip(upper=100)

    work = work[work["_skill_count"] > 0]
    work = work.sort_values(["_match_percent", "_skill_count"], ascending=False)

    if title_col:
        work = work.drop_duplicates(subset=[title_col])

    work = work.head(15)

    result = pd.DataFrame()
    result["Match %"] = work["_match_percent"]
    result["Matching Skills"] = work["_matched_skills"].apply(lambda s: ", ".join(s))

    if title_col:
        result["Job Title"] = work[title_col].fillna("Not listed")
    if company_col:
        result["Company"] = work[company_col].fillna("Not listed")
    if city_col:
        result["City"] = work[city_col].fillna("Not listed")
    if department_col:
        result["Department"] = work[department_col].fillna("Not listed")
    if experience_col:
        result["Experience Required"] = work[experience_col].fillna("Not listed")
    if description_col:
        result["Job Description"] = (
            work[description_col].fillna("").astype(str).str.slice(0, 300)
        )
    if link_col:
        result["Application Link"] = work[link_col].fillna("Not listed")

    return result, cv_skills


def render_job_card(row):
    score = int(row.get("Match %", 0))
    tier = "hi" if score >= 60 else "mid" if score >= 30 else "lo"
    title = esc(row.get("Job Title", "Untitled role"))

    meta_parts = [
        str(row[k]) for k in ("Company", "City", "Experience Required")
        if k in row and str(row[k]) != "Not listed"
    ]
    meta = esc("  |  ".join(meta_parts)) if meta_parts else "Details not listed"

    skills = [s for s in str(row.get("Matching Skills", "")).split(", ") if s]
    desc = str(row.get("Job Description", "")).strip()
    desc_html = f'<p class="desc">{esc(desc)}...</p>' if desc else ""

    link = str(row.get("Application Link", ""))
    link_html = ""
    if link.startswith(("http://", "https://")):
        link_html = f'<a class="apply" href="{esc(link)}" target="_blank" rel="noopener">Open application page</a>'

    st.markdown(
        f"""
        <div class="job">
            <div>
                <h4>{title}</h4>
                <div class="meta">{meta}</div>
                {chips_html(skills, "teal")}
                {desc_html}
                {link_html}
            </div>
            <div class="score {tier}">{score}%<small>match</small></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
online = ollama_online()

with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="logo">🧭</div>'
        '<div class="name">Career Compass</div></div>'
        '<div class="brand-sub">Local AI career assistant</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-label">MODEL</div>', unsafe_allow_html=True)
    model = st.text_input("Ollama model", value="qwen2.5:3b", label_visibility="collapsed")

    def status(ok, text):
        return (
            f'<div class="status-row"><span class="dot {"ok" if ok else "bad" if ok is False else ""}"></span>'
            f"{esc(text)}</div>"
        )

    st.markdown('<div class="side-label">STATUS</div>', unsafe_allow_html=True)
    st.markdown(
        status(online, "Ollama running" if online else "Ollama offline")
        + status(bool(st.session_state.cv_text) or None,
                 f"CV: {st.session_state.cv_name}" if st.session_state.cv_text else "No CV uploaded")
        + status(bool(st.session_state.cv_analysis) or None,
                 "CV analyzed" if st.session_state.cv_analysis else "CV not analyzed yet")
        + status(st.session_state.matches is not None and not st.session_state.matches.empty or None,
                 "Jobs matched" if st.session_state.matches is not None else "Jobs not matched yet"),
        unsafe_allow_html=True,
    )

    if not online:
        st.caption("Open the Ollama desktop app, then refresh this page.")

    st.markdown('<div class="side-label">PRIVACY</div>', unsafe_allow_html=True)
    st.caption("Your CV never leaves this computer. The model runs locally through Ollama.")

# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
        <div>
            <h1>Career Compass</h1>
            <p>Upload your CV, see how it reads, match it with real Pakistan job
            listings and talk to a local AI mentor. All in one place.</p>
        </div>
        <div class="hero-badge">{esc(model)} - local</div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_cv, tab_jobs, tab_chat = st.tabs(
    ["CV Analyzer", "Job Recommendations", "Career Chatbot"]
)

# ----------------------------------------------------------------------------
# Tab 1: CV Analyzer
# ----------------------------------------------------------------------------
with tab_cv:
    section("Analyze your CV", "Upload a PDF, DOCX or TXT file to get structured feedback.")

    cv_file = st.file_uploader(
        "Choose your CV",
        type=["pdf", "docx", "txt"],
        key="cv_upload",
        label_visibility="collapsed",
    )

    if cv_file:
        extracted = extract_text(cv_file)

        if not extracted.strip():
            st.warning(
                "No text found in this file. If it's a scanned PDF, "
                "you'll need OCR or a text-based version."
            )
        else:
            if st.session_state.cv_name != cv_file.name:
                st.session_state.cv_analysis = ""
                st.session_state.matches = None
            st.session_state.cv_text = extracted
            st.session_state.cv_name = cv_file.name

            found_skills = find_terms(extracted, SKILLS)
            found_roles = find_terms(extracted, ROLE_TERMS)

            stat_cards([
                (len(extracted.split()), "Words in CV"),
                (len(found_skills), "Skills detected"),
                (len(found_roles), "Role keywords"),
                (cv_file.name.rsplit(".", 1)[-1].upper(), "File type"),
            ])

            left, right = st.columns([3, 2], gap="medium")
            with left:
                st.markdown(
                    '<div class="panel"><div class="panel-title">Skills found in your CV</div>'
                    + chips_html(found_skills)
                    + "</div>",
                    unsafe_allow_html=True,
                )
            with right:
                st.markdown(
                    '<div class="panel"><div class="panel-title">Roles mentioned</div>'
                    + chips_html(found_roles, "teal")
                    + "</div>",
                    unsafe_allow_html=True,
                )

            with st.expander("Preview extracted text"):
                st.text(extracted[:5000])

            if st.button("Analyze my CV", type="primary"):
                prompt = (
                    "Analyze this resume. Use these headings: Profile Summary, "
                    "Education, Skills Found, Experience, Strengths, "
                    "Missing Skills, Skills to Learn, Suitable CS/IT/AI/SE Roles. "
                    "Do not invent details. Resume:\n\n" + extracted[:12000]
                )
                with st.spinner("Reading your CV with the local model..."):
                    try:
                        result = ask_ollama(
                            [
                                {
                                    "role": "system",
                                    "content": "Analyze only the supplied CV. Do not invent facts.",
                                },
                                {"role": "user", "content": prompt},
                            ],
                            model,
                        )
                        st.session_state.cv_analysis = result
                        st.rerun()
                    except requests.exceptions.ConnectionError:
                        st.error("Can't reach Ollama. Open the Ollama app and try again.")
                    except Exception as exc:
                        st.error(f"Analysis failed: {exc}")

    if st.session_state.cv_analysis:
        st.markdown(
            '<div class="panel-title" style="margin-top:10px">AI analysis</div>',
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            st.markdown(st.session_state.cv_analysis)
        st.success("Analysis saved. Open Job Recommendations next.")
    elif not cv_file:
        st.info("Upload a CV to get started.")

# ----------------------------------------------------------------------------
# Tab 2: Job Recommendations
# ----------------------------------------------------------------------------
with tab_jobs:
    section(
        "Jobs that fit your CV",
        "Ranked by how many of your skills appear in each listing.",
    )

    with st.expander("Jobs dataset", expanded=False):
        jobs_upload = st.file_uploader(
            "Upload the Pakistan jobs CSV if it isn't found automatically",
            type=["csv"],
            key="jobs_upload",
        )

    jobs_df = load_jobs(jobs_upload)

    if jobs_df is not None:
        st.caption(f"{len(jobs_df):,} jobs loaded from the dataset.")
    else:
        st.warning(
            "Jobs CSV not found. Upload it above or place it in the project folder."
        )

    if not st.session_state.cv_text:
        st.info("Upload your CV in the CV Analyzer tab first.")
    else:
        if st.button("Find matching jobs", type="primary", disabled=jobs_df is None):
            with st.spinner("Matching your skills against job listings..."):
                matches, detected = recommend_jobs(jobs_df, st.session_state.cv_text)
            st.session_state.matches = matches
            st.session_state.detected_skills = detected

        matches = st.session_state.matches

        if matches is not None:
            detected = st.session_state.detected_skills

            if matches.empty:
                st.warning(
                    "No jobs matched your skills. Check that your CV lists skills "
                    "like Python or SQL, and that the jobs CSV is the right file."
                )
            else:
                stat_cards([
                    (len(matches), "Jobs recommended"),
                    (len(detected), "Skills used"),
                    (f"{int(matches['Match %'].max())}%", "Best match"),
                    (f"{int(matches['Match %'].mean())}%", "Average match"),
                ])
                st.markdown(
                    '<div class="panel"><div class="panel-title">Skills used for matching</div>'
                    + chips_html(detected)
                    + "</div>",
                    unsafe_allow_html=True,
                )
                st.caption(
                    "Match % is a keyword-overlap estimate. It is not the "
                    "probability of getting the job."
                )

                view = st.radio(
                    "View",
                    ["Cards", "Table"],
                    horizontal=True,
                    label_visibility="collapsed",
                )

                if view == "Cards":
                    for _, row in matches.iterrows():
                        render_job_card(row)
                else:
                    config = {
                        "Match %": st.column_config.ProgressColumn(
                            "Match", min_value=0, max_value=100, format="%d%%"
                        )
                    }
                    if "Application Link" in matches.columns:
                        config["Application Link"] = st.column_config.LinkColumn("Apply")
                    st.dataframe(
                        matches,
                        use_container_width=True,
                        hide_index=True,
                        column_config=config,
                    )

                st.download_button(
                    "Download results (CSV)",
                    matches.to_csv(index=False).encode("utf-8"),
                    file_name="career_compass_job_matches.csv",
                    mime="text/csv",
                )

# ----------------------------------------------------------------------------
# Tab 3: Chatbot
# ----------------------------------------------------------------------------
def build_chat_messages():
    system = (
        "You are Career Compass, a friendly career mentor for CS, IT, AI and "
        "software engineering students in Pakistan. Give short, practical answers. "
        "Reply in the same language the user writes in (English or Roman Urdu)."
    )
    if st.session_state.cv_text:
        system += "\n\nThe user's CV (excerpt):\n" + st.session_state.cv_text[:1200]
    history = [m for m in st.session_state.messages[-8:]]
    return [{"role": "system", "content": system}] + history


with tab_chat:
    head_l, head_r = st.columns([4, 1])
    with head_l:
        section(
            "Ask Career Compass",
            "Career advice, interview prep and learning paths."
            + (" Your CV is used as context." if st.session_state.cv_text else ""),
        )
    with head_r:
        if st.button("New chat", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": GREETING}]
            st.session_state.pop("queued", None)
            st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if len(st.session_state.messages) == 1 and "queued" not in st.session_state:
        st.caption("Try one of these:")
        cols = st.columns(2)
        for i, text in enumerate(SUGGESTIONS):
            if cols[i % 2].button(text, key=f"sugg_{i}", use_container_width=True):
                st.session_state.queued = text
                st.rerun()

    prompt = st.chat_input("Ask a career question...") or st.session_state.pop("queued", None)

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Thinking...")

            try:
                answer = ask_ollama(build_chat_messages(), model, num_predict=256)
                placeholder.markdown(answer or "The model returned an empty response.")
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer or "(empty response)"}
                )
            except requests.exceptions.ConnectionError:
                placeholder.error("Can't reach Ollama. Open the Ollama app and try again.")
            except Exception as exc:
                placeholder.error(f"Something went wrong: {exc}")

st.markdown(
    '<div class="footer-note">Career Compass - runs fully offline with Ollama</div>',
    unsafe_allow_html=True,
)