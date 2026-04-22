import streamlit as st
import requests

st.set_page_config(page_title="AI Sales Outreach", page_icon="🚀")
st.title("🚀 AI Sales Outreach Platform")

BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")

tab1, tab2 = st.tabs(["Single Outreach", "Bulk Outreach"])

# -------------------------
# Single Outreach Tab
# -------------------------
with tab1:
    st.subheader("Generate a Personalized Outreach Message")

    name     = st.text_input("Lead Name")
    role     = st.text_input("Role / Title")
    company  = st.text_input("Company")
    industry = st.text_input("Industry")
    product  = st.text_input("Your Product")
    tone     = st.selectbox("Tone", ["Professional", "Friendly", "Casual", "Formal"])

    if st.button("Generate Outreach"):
        if not all([name, role, company, industry, product, tone]):
            st.warning("Please fill in all fields.")
        else:
            with st.spinner("Generating..."):
                try:
                    res = requests.post(f"{BACKEND_URL}/generate-outreach", json={
                        "name": name, "role": role, "company": company,
                        "industry": industry, "product": product, "tone": tone
                    })
                    res.raise_for_status()
                    data = res.json()

                    st.success("✅ Outreach Generated!")
                    st.json(data["data"])

                    score = data["personalization_score"]
                    st.metric(
                        "Personalization Score",
                        f"{score['score']}/{score['out_of']} ({score['percentage']}%)"
                    )
                    with st.expander("Score Breakdown"):
                        for field, hit in score["details"].items():
                            st.write(f"{'✅' if hit else '❌'} {field.capitalize()} mentioned")

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend. Make sure the FastAPI server is running.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# -------------------------
# Bulk Outreach Tab
# -------------------------
with tab2:
    st.subheader("Upload a CSV for Bulk Outreach")
    product_bulk = st.text_input("Product Name (for bulk)", value="AI Sales Tool")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if st.button("Process Bulk CSV"):
        if uploaded_file is None:
            st.warning("Please upload a CSV file.")
        else:
            with st.spinner("Processing..."):
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/bulk-outreach",
                        files={"file": (uploaded_file.name, uploaded_file, "text/csv")},
                        params={"product": product_bulk}
                    )
                    res.raise_for_status()
                    data = res.json()

                    st.success(f"✅ Processed {len(data['processed_leads'])} leads!")
                    st.json(data["processed_leads"])

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend. Make sure the FastAPI server is running.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
