from fastapi import FastAPI, File, UploadFile, HTTPException
from extractor import extract_text_from_pdf
from fraud_checker import analyze_resume_text
import shutil
import os
import uuid
from datetime import datetime

app = FastAPI(title="Enterprise Resume Risk Analysis API")


@app.post("/analyze-resume")
async def analyze_resume(file: UploadFile = File(...)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    resume_id = f"RES-{uuid.uuid4().hex[:8].upper()}"
    file_location = f"temp_{resume_id}.pdf"

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = extract_text_from_pdf(file_location)

        if not text.strip():
            raise HTTPException(status_code=400, detail="Text extraction failed")

        result = analyze_resume_text(text)

        return {
            "status": "SUCCESS",
            "timestamp": datetime.utcnow().isoformat(),
            "resume_id": resume_id,
            "analysis": result["analysis"],
            "verification": result["verification"],
            "flags": result["flags"]
        }

    finally:
        if os.path.exists(file_location):
            os.remove(file_location)
