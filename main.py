import streamlit as st
import os
import json
import pandas as pd
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# Page Config
# -------------------------
st.set_page_config(
    page_title="AI Sales Outreach",
    page_icon="🚀",
    layout="wide"
)

# -------------------------
# Custom Styling
# -------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Syne', sans-serif !important; }
    .stApp { background: #0a0a0f; color: #e8e8f0; }
    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        background: #14141f !important;
        border: 1px solid #2a2a3f !important;
        color: #e8e8f0 !important;
        border-radius: 8px !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #6c63ff, #a855f7) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.6rem 2rem !important;
        width: 100%;
    }
    .result-box {
        background: #14141f;
        border: 1px solid #2a2a3f;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        white-space: pre-wrap;
        line-height: 1.7;
        color: #e8e8f0;
    }
    .score-pill { display: inline-block; border-radius: 999px; padding: 0.3rem 1rem; font-family: 'Syne', sans-serif; font-weight: 600; margin: 0.25rem; font-size: 0.85rem; }
    .score-pill.hit { border: 1px solid #22c55e66; color: #4ade80; background: #22c55e11; }
    .score-pill.miss { border: 1px solid #ef444466; color: #f87171; background: #ef444411; }
    .header-title { font-family: 'Syne', sans-serif; font-size: 2.8rem; font-weight: 800; background: linear-gradient(135deg, #6c63ff, #a855f7, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.2rem; }
    .header-sub { color: #666; font-size: 1rem; margin-bottom: 2rem; }
    label { color: #aaa !important; font-size: 0.85rem !important; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# OpenAI Client
# -------------------------
api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
client = OpenAI(api_key=api_key) if api_key else None

# -------------------------
# Helper Functions
# -------------------------
def build_prompt(name, role, company, industry, product, tone):
    return f"""
You are an expert B2B sales copywriter. Write a highly personalized outreach message.

Lead Details:
- Name: {name}
- Role: {role}
- Company: {company}
- Industry: {industry}

Product to pitch: {product}
Tone: {tone}

Return ONLY a valid JSON object with these keys:
- "subject": email subject line
- "body": the full outreach email body
- "cta": a one-line call to action

No extra text, no markdown, no code fences.
"""

def personalization_score(text, name, company, role, industry):
    text_lower = text.lower()
    checks = {
        "Name": name.lower() in text_lower,
        "Company": company.lower() in text_lower,
        "Role": role.lower() in text_lower,
        "Industry": industry.lower() in text_lower,
    }
    score = sum(checks.values())
    return score, len(checks), checks

def generate_outreach(name, role, company, industry, product, tone):
    if not client:
        st.error("No OpenAI API key found. Add OPENAI_API_KEY to Streamlit secrets.")
        return None
    prompt = build_prompt(name, role, company, industry, product, tone)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        result = response.choices[0].message.content
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"subject": "", "body": result, "cta": ""}
    except OpenAIError as e:
        st.error(f"OpenAI error: {e}")
        return None

# -------------------------
# Header
# -------------------------
st.markdown('<div class="header-title">🚀 AI Sales Outreach</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">Generate personalized outreach messages powered by AI</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["✉️  Single Outreach", "📂  Bulk CSV Outreach"])

# -------------------------
# Tab 1: Single Outreach
# -------------------------
with tab1:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("#### Lead Details")
        name     = st.text_input("Full Name", placeholder="e.g. Sarah Johnson")
        role     = st.text_input("Job Title", placeholder="e.g. VP of Marketing")
        company  = st.text_input("Company", placeholder="e.g. Acme Corp")
        industry = st.text_input("Industry", placeholder="e.g. SaaS / FinTech")
        product  = st.text_input("Your Product", placeholder="e.g. AI analytics platform")
        tone     = st.selectbox("Tone", ["Professional", "Friendly", "Casual", "Formal", "Concise"])
        generate_btn = st.button("✨ Generate Outreach")

    with col2:
        st.markdown("#### Generated Message")
        if generate_btn:
            if not all([name, role, company, industry, product]):
                st.warning("Please fill in all fields.")
            else:
                with st.spinner("Writing your personalized outreach..."):
                    result = generate_outreach(name, role, company, industry, product, tone)
                if result:
                    if result.get("subject"):
                        st.markdown(f"**Subject:** {result['subject']}")
                    st.markdown(f'<div class="result-box">{result.get("body", "")}</div>', unsafe_allow_html=True)
                    if result.get("cta"):
                        st.info(f"**CTA:** {result['cta']}")
                    score, total, checks = personalization_score(
                        result.get("body", ""), name, company, role, industry
                    )
                    st.markdown(f"**Personalization Score: {score}/{total} ({round(score/total*100)}%)**")
                    pills = "".join([
                        f'<span class="score-pill {"hit" if hit else "miss"}">{"✓" if hit else "✗"} {field}</span>'
                        for field, hit in checks.items()
                    ])
                    st.markdown(pills, unsafe_allow_html=True)
        else:
            st.markdown('<div class="result-box" style="color:#444;font-style:italic;">Your generated outreach will appear here...</div>', unsafe_allow_html=True)

# -------------------------
# Tab 2: Bulk CSV Outreach
# -------------------------
with tab2:
    st.markdown("#### Upload your leads CSV")
    st.caption("Required columns: `name`, `role`, `company`, `industry` — optional: `product`, `tone`")

    product_default = st.text_input("Default Product", value="AI Sales Tool")
    tone_default    = st.selectbox("Default Tone", ["Professional", "Friendly", "Casual", "Formal"])
    uploaded_file   = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.lower()
        required_cols = {"name", "role", "company", "industry"}
        missing = required_cols - set(df.columns)

        if missing:
            st.error(f"CSV is missing columns: {', '.join(missing)}")
        else:
            st.success(f"✅ Loaded {len(df)} leads")
            st.dataframe(df.head(), use_container_width=True)

            if st.button("🚀 Generate Bulk Outreach"):
                if not client:
                    st.error("No OpenAI API key found.")
                else:
                    results = []
                    progress = st.progress(0, text="Processing leads...")
                    for i, row in df.iterrows():
                        p = row.get("product", product_default)
                        t = row.get("tone", tone_default)
                        out = generate_outreach(row["name"], row["role"], row["company"], row["industry"], p, t)
                        if out:
                            score, total, _ = personalization_score(
                                out.get("body", ""), row["name"], row["company"], row["role"], row["industry"]
                            )
                            results.append({
                                "name": row["name"],
                                "company": row["company"],
                                "subject": out.get("subject", ""),
                                "body": out.get("body", ""),
                                "cta": out.get("cta", ""),
                                "score": f"{score}/{total}",
                            })
                        progress.progress((i + 1) / len(df), text=f"Processing {i+1}/{len(df)}...")
                    progress.empty()
                    results_df = pd.DataFrame(results)
                    st.success(f"✅ Generated {len(results_df)} outreach messages!")
                    st.dataframe(results_df, use_container_width=True)
                    st.download_button(
                        "⬇️ Download Results CSV",
                        data=results_df.to_csv(index=False).encode("utf-8"),
                        file_name="outreach_results.csv",
                        mime="text/csv"
                    )
