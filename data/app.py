import numpy as np
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ai import rank_candidates, analyze_resume, classify_batch, ask_data
import style

st.set_page_config(page_title="ResumeIQ", page_icon="📄", layout="wide")
style.inject_css()
style.sidebar()
style.hero()

NAVY = "#0B1F4B"


# ---------------- Data + Search Index ----------------
@st.cache_data
def load_data():
    return pd.read_csv("data/resumes_clean.csv")


@st.cache_resource
def build_index(texts):
    vec = TfidfVectorizer(stop_words="english", max_features=5000, ngram_range=(1, 2))
    mat = vec.fit_transform(texts)
    return vec, mat


df = load_data()
vec, mat = build_index(tuple(df["Resume"]))
categories = sorted(df["Category"].unique())


def top_terms_per_category(n=8):
    terms = np.array(vec.get_feature_names_out())
    out = {}
    for c in categories:
        idx = np.where(df["Category"] == c)[0]
        mean = np.asarray(mat[idx].mean(axis=0)).ravel()
        out[c] = ", ".join(terms[mean.argsort()[::-1][:n]])
    return out


@st.cache_data(show_spinner=False)
def cached_rank(job_desc, ids):
    rows = df[df["resume_id"].isin(ids)]
    items = [{"id": int(r.resume_id), "category": r.Category, "resume": r.Resume[:1500]}
             for r in rows.itertuples()]
    return rank_candidates(job_desc, items)


@st.cache_data(show_spinner=False)
def cached_analyze(text):
    return analyze_resume(text)


tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Dashboard", "🎯 Job Matcher", "🙋‍♀️ Resume Analyzer", "💬 Ask AI"])

# ================= TAB 1: Dashboard =================
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    style.kpi(c1, "📄", "Unique resumes", len(df))
    style.kpi(c2, "🗂️", "Job categories", len(categories))
    style.kpi(c3, "📏", "Avg length (chars)", int(df["length"].mean()))
    style.kpi(c4, "🧹", "Duplicates removed", 962 - len(df))

    style.section("Category distribution")
    st.bar_chart(df["Category"].value_counts(), color=NAVY)

    style.note("🔎 Data cleaning insight: original file mein 962 rows thin, lekin duplicate resumes "
               "hatane ke baad sirf 166 unique bachay. Duplicates se analysis galat hoti hai.")

    style.section("Har category ke top keywords (TF-IDF)")
    st.dataframe(pd.DataFrame(top_terms_per_category().items(),
                              columns=["Category", "Top keywords"]), hide_index=True)

    style.section("🧪 AI Accuracy Test")
    st.write("AI ko kuch resumes bina label ke diye jate hain, phir uska jawab asal label se milaya jata hai.")
    n = st.slider("Kitne resumes test karein?", 5, 20, 10)
    if st.button("Run accuracy test"):
        sample = df.sample(n, random_state=1)
        items = [{"id": int(r.resume_id), "resume": r.Resume[:700]} for r in sample.itertuples()]
        with st.spinner("AI classify kar raha hai..."):
            try:
                res = pd.DataFrame(classify_batch(items, categories)).rename(
                    columns={"id": "resume_id", "category": "AI_category"})
                cmp = sample[["resume_id", "Category"]].merge(res, on="resume_id")
                cmp["Correct"] = cmp["Category"] == cmp["AI_category"]
                a, b = st.columns(2)
                style.kpi(a, "🎯", "AI Accuracy", f"{cmp['Correct'].mean() * 100:.0f}%")
                style.kpi(b, "🧾", "Resumes tested", len(cmp))
                st.write("")
                st.dataframe(cmp, hide_index=True)
            except Exception as e:
                st.error(f"Error: {e}")

# ================= TAB 2: Job Matcher =================
with tab2:
    style.section("Job description likhein, best candidates dhoondein")
    example = ("We need a Python Data Scientist with machine learning, pandas, scikit-learn, "
               "SQL and NLP experience. 2+ years experience.")
    jd = st.text_area("Job description", value=example, height=120)
    k = st.slider("AI kitne top candidates score kare?", 5, 15, 10)

    if st.button("🔍 Find best candidates") and jd.strip():
        sims = cosine_similarity(vec.transform([jd]), mat).ravel()
        top_idx = sims.argsort()[::-1][:k]
        top_df = df.iloc[top_idx].copy()
        top_df["keyword_similarity"] = (sims[top_idx] * 100).round(1)

        with st.spinner("Gemini AI score kar raha hai..."):
            try:
                res = pd.DataFrame(cached_rank(jd, tuple(int(i) for i in top_df["resume_id"]))
                                   ).rename(columns={"id": "resume_id"})
                out = top_df.merge(res, on="resume_id").sort_values("score", ascending=False)
                a, b, c = st.columns(3)
                style.kpi(a, "✅", "Shortlist", int((out["recommendation"] == "Shortlist").sum()))
                style.kpi(b, "🤔", "Maybe", int((out["recommendation"] == "Maybe").sum()))
                style.kpi(c, "🏆", "Best score", int(out["score"].max()))

                style.section("Top candidates")
                for rank, (_, row) in enumerate(out.iterrows(), start=1):
                    style.candidate_card(rank, row)

                style.section("Score chart")
                st.bar_chart(out.set_index("resume_id")["score"], color=NAVY)

                st.download_button("⬇️ Download results CSV",
                                   out.drop(columns=["Resume"]).to_csv(index=False).encode("utf-8"),
                                   file_name="shortlist.csv", mime="text/csv")
                with st.expander("Top resume ka text dekhein"):
                    st.text(out.iloc[0]["Resume"][:2500])
            except Exception as e:
                st.warning(f"AI nahi chala ({e}). Neeche sirf keyword-based ranking hai.")
                st.dataframe(top_df[["resume_id", "Category", "keyword_similarity"]],
                             hide_index=True)

# ================= TAB 3: Resume Analyzer =================
with tab3:
    style.section("Apna resume do, AI feedback dega")
    up = st.file_uploader("PDF ya TXT upload karein (optional)", type=["pdf", "txt"])
    text = ""
    if up is not None:
        if up.name.lower().endswith(".pdf"):
            from pypdf import PdfReader
            text = "\n".join((p.extract_text() or "") for p in PdfReader(up).pages)
        else:
            text = up.read().decode("utf-8", errors="ignore")
    text = st.text_area("Ya yahan resume paste karein", value=text, height=220)

    if st.button("✨ Analyse my resume") and text.strip():
        with st.spinner("AI analyse kar raha hai..."):
            try:
                r = cached_analyze(text)
                a, b, c = st.columns(3)
                style.kpi(a, "📈", "ATS score", f"{r['ats_score']}/100")
                style.kpi(b, "🧭", "Best field", r["predicted_category"])
                style.kpi(c, "⏳", "Experience (yrs)", r["experience_years"])
                st.progress(min(int(r["ats_score"]), 100) / 100)
                style.note("Summary: " + str(r["summary"]))
                style.note("Top skills: " + str(r["top_skills"]))
                x, y = st.columns(2)
                with x:
                    style.result_card("✅ Strengths", r["strengths"])
                with y:
                    style.result_card("🛠️ Improvements", r["improvements"])
                style.result_card("💼 Suggested roles", r["suggested_roles"])
                st.success(r["encouragement"])
            except Exception as e:
                st.error(f"Error: {e}")

# ================= TAB 4: Ask AI =================
with tab4:
    style.section("Dataset ke baare mein sawal poochein")
    lines = [f"Total unique resumes: {len(df)}"]
    kw = top_terms_per_category()
    for c, cnt in df["Category"].value_counts().items():
        lines.append(f"Category {c}: resumes={cnt}, top_keywords={kw[c]}")
    stats_text = "\n".join(lines)
    with st.expander("AI ko ye summary di ja rahi hai"):
        st.text(stats_text)

    q = st.text_input("Sawal", placeholder="Data Science ke liye kaun si skills sab se zyada hain?")
    if st.button("Poochein") and q:
        with st.spinner("..."):
            try:
                style.note(ask_data(q, stats_text))
            except Exception as e:
                st.error(f"Error: {e}")

style.footer()