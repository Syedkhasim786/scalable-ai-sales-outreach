# Scalable AI Sales Outreach

An AI-powered sales outreach platform built with FastAPI and OpenAI.

## Features
- Single lead outreach generation
- Bulk CSV outreach processing
- Personalization scoring

## Setup

1. Clone the repo
2. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_key_here
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the FastAPI server:
   ```
   uvicorn main:app --reload
   ```
5. Run the Streamlit frontend (optional):
   ```
   streamlit run streamlit_app.py
   ```

## Deployment
- **Backend (FastAPI):** Deploy on Render or Railway
- **Frontend (Streamlit):** Deploy on Streamlit Cloud, set main file to `streamlit_app.py`
