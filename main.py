from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv
import openai
import shutil
from prompt import build_prompt
from bulk_processor import process_csv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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
def personalization_score(text, name, company):
    score = 0
    if name.lower() in text.lower():
        score += 1
    if company.lower() in text.lower():
        score += 1
    return score


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
        lead.tone
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    result = response["choices"][0]["message"]["content"]

    try:
        parsed = json.loads(result)
    except:
        parsed = {"raw_output": result}

    score = personalization_score(result, lead.name, lead.company)

    return {
        "data": parsed,
        "personalization_score": score
    }


# -------------------------
# Bulk Outreach
# -------------------------
@app.post("/bulk-outreach")
def bulk_outreach(file: UploadFile = File(...)):

    file_location = f"temp_{file.filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    data = process_csv(file_location, "AI Sales Tool")

    return {"processed_leads": data}
