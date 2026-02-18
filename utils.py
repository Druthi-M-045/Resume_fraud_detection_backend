# utils.py
import logging
import os
from fastapi import HTTPException

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# PDF validation
def validate_pdf(filename: str):
    if not filename.lower().endswith(".pdf"):
        logger.warning(f"File validation failed: {filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

# Simple JWT mockup (for demonstration, replace with real JWT in production)
import base64
import json

def create_token(user):
    payload = json.dumps({"username": user["username"], "role": user["role"]})
    token = base64.b64encode(payload.encode()).decode()
    return token

def decode_token(token: str):
    try:
        payload = base64.b64decode(token.encode()).decode()
        return json.loads(payload)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
