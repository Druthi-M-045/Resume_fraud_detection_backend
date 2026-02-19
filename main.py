from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
import shutil
import os
from auth import get_current_user, login, signup
from utils import validate_pdf, UPLOAD_FOLDER, logger
from database import reports, users
from models import UserLogin
from extractor import extract_text_from_pdf
from fraud_checker import analyze_resume_text

app = FastAPI(title="Resume Fraud Detection")

# ---------------- Signup ----------------
@app.post("/signup")
def signup_user(data: UserLogin):
    # Check if username exists
    existing_user = next((u for u in users if u["username"] == data.username), None)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Add new user
    new_user = {"username": data.username, "password": data.password, "role": "user"}
    users.append(new_user)
    return {"message": "User created successfully", "username": data.username, "role": "user"}

# ---------------- Login ----------------
@app.post("/login")
def login_user(data: UserLogin):
    user = next((u for u in users if u["username"] == data.username and u["password"] == data.password), None)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login successful", "username": user["username"], "role": user["role"]}

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
def analyze_resume(filename: str):
    # Check if file exists
    file_path = f"{UPLOAD_FOLDER}/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Resume '{filename}' not found")
    
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(file_path)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Analyze resume for fraud
        analysis_results = analyze_resume_text(text)
        
        logger.info(f"Analyzed resume: {filename}")
        return analysis_results
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing resume {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")

# ---------------- Reports (Admin Only) ----------------
@app.get("/reports")
def get_reports(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return reports
