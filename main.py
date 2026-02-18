from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
import shutil
from auth import get_current_user, login, signup
from utils import validate_pdf, UPLOAD_FOLDER, logger
from database import reports, users
from models import UserLogin

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

# ---------------- Reports (Admin Only) ----------------
@app.get("/reports")
def get_reports(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return reports
