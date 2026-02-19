from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from auth import get_current_user, router as auth_router
from utils import validate_pdf, UPLOAD_FOLDER, logger
from database import reports
from extractor import extract_text_from_pdf
from fraud_checker import analyze_resume_text

app = FastAPI(title="Resume Fraud Detection")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

# ---------------- Get User Profile ----------------
@app.get("/getuser")
def get_user_profile(current_user: dict = Depends(get_current_user)):
    return current_user

# ---------------- Upload Resume ----------------
@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Only users can upload resumes")

    # Validate PDF
    validate_pdf(file.filename)

    # Save file
    file_path = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Save report
    reports.append({"filename": file.filename, "uploaded_by": current_user["username"]})
    logger.info(f"{current_user['username']} uploaded {file.filename}")

    return {"message": f"{file.filename} uploaded successfully", "uploaded_by": current_user["username"]}

# ---------------- Analyze Resume ----------------
@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    try:
        # Save temporary file
        temp_path = f"{UPLOAD_FOLDER}/temp_{file.filename}"
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Extract text from PDF
        text = extract_text_from_pdf(temp_path)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Analyze resume for fraud
        analysis_results = analyze_resume_text(text)
        
        logger.info(f"Analyzed resume: {file.filename}")
        return analysis_results
    
    except Exception as e:
        logger.error(f"Error analyzing resume {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")

# ---------------- Reports (Admin Only) ----------------
@app.get("/reports")
def get_reports(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return reports
