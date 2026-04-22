from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
import shutil
from prompt import build_prompt
from bulk_processor import process_csv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# -------------------------
# Input Model
# -------------------------
class Lead(BaseModel):
    name: str
    role: str
    company: str
    industry: str
    product: str
    tone: str

# -------------------------
# Home Route
# -------------------------
@app.get("/")
def home():
    return {"message": "Scalable AI Sales Outreach Platform Running 🚀"}

# -------------------------
# Personalization Score
# -------------------------
def personalization_score(text: str, name: str, company: str, role: str, industry: str) -> dict:
    text_lower = text.lower()
    checks = {
        "name": name.lower() in text_lower,
        "company": company.lower() in text_lower,
        "role": role.lower() in text_lower,
        "industry": industry.lower() in text_lower,
    }
    score = sum(checks.values())
    return {
        "score": score,
        "out_of": len(checks),
        "percentage": round((score / len(checks)) * 100),
        "details": checks,
    }

# -------------------------
# Single Outreach
# -------------------------
@app.post("/generate-outreach")
def generate_outreach(lead: Lead):
    prompt = build_prompt(
        lead.name,
        lead.role,
        lead.company,
        lead.industry,
        lead.product,
        lead.tone,
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
    except OpenAIError as e:
        raise HTTPException(status_code=502, detail=f"OpenAI API error: {str(e)}")

    result = response.choices[0].message.content

    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        parsed = {"raw_output": result}

    score = personalization_score(result, lead.name, lead.company, lead.role, lead.industry)

    return {
        "data": parsed,
        "personalization_score": score,
    }

# -------------------------
# Bulk Outreach
# -------------------------
@app.post("/bulk-outreach")
def bulk_outreach(
    file: UploadFile = File(...),
    product: str = Query(default="AI Sales Tool", description="Product name to use for outreach"),
):
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported.")

    file_location = f"temp_{file.filename}"

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        data = process_csv(file_location, product)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        if os.path.exists(file_location):
            os.remove(file_location)

    return {"processed_leads": data}
