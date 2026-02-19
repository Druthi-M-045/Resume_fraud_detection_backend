import re
import requests
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ------------------------------
# GitHub Verification
# ------------------------------
def verify_github(text):
    github_match = re.search(r"github\.com/([A-Za-z0-9_-]+)", text)

    if not github_match:
        return {"found": False, "valid": False, "score": 0}

    username = github_match.group(1)

    try:
        response = requests.get(f"https://api.github.com/users/{username}")
        if response.status_code != 200:
            return {"found": True, "valid": False, "score": 0}

        data = response.json()
        score = 0

        if data["public_repos"] >= 3:
            score += 15
        if data["followers"] >= 5:
            score += 10

        account_age = datetime.now() - datetime.strptime(
            data["created_at"], "%Y-%m-%dT%H:%M:%SZ"
        )
        if account_age.days > 90:
            score += 10

        return {"found": True, "valid": True, "score": score}

    except:
        return {"found": True, "valid": False, "score": 0}


# ------------------------------
# LinkedIn Verification
# ------------------------------
def verify_linkedin(text):
    pattern = r"https:\/\/(www\.)?linkedin\.com\/in\/[A-Za-z0-9_-]+"
    return bool(re.search(pattern, text))


# ------------------------------
# Contact Validation
# ------------------------------
def validate_contact(text):
    email_pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    phone_pattern = r"\b\d{10}\b"

    return {
        "email_valid": bool(re.search(email_pattern, text)),
        "phone_valid": bool(re.search(phone_pattern, text))
    }


# ------------------------------
# AI Detection (Advanced Heuristic)
# ------------------------------
def detect_ai_content(text):

    generic_phrases = [
        "highly motivated",
        "detail oriented",
        "passionate individual",
        "results driven",
        "team player",
    ]

    score = 0
    text_lower = text.lower()

    for phrase in generic_phrases:
        if phrase in text_lower:
            score += 10

    if not re.search(r"\d+", text):
        score += 20

    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 10]

    if len(sentences) > 5:
        vectorizer = TfidfVectorizer().fit_transform(sentences)
        similarity = cosine_similarity(vectorizer).mean()
        if similarity > 0.7:
            score += 20

    return score


# ------------------------------
# Main Enterprise Analysis
# ------------------------------
def analyze_resume_text(text):

    fraud_score = 0
    flags = []

    # GitHub
    github_result = verify_github(text)
    if not github_result["valid"]:
        fraud_score += 40
        flags.append("Invalid GitHub account")

    # LinkedIn
    linkedin_valid = verify_linkedin(text)
    if not linkedin_valid:
        fraud_score += 15
        flags.append("LinkedIn profile missing or invalid")

    # Contact
    contact_info = validate_contact(text)
    if not contact_info["email_valid"] or not contact_info["phone_valid"]:
        fraud_score += 15
        flags.append("Missing valid contact information")

    # AI Detection
    ai_score = detect_ai_content(text)
    if ai_score > 40:
        fraud_score += 40
        flags.append("AI-generated content suspected")

    # Risk Level Logic
    if fraud_score >= 70:
        risk = "HIGH"
        decision = "REJECT"
        confidence = 0.90
    elif fraud_score >= 40:
        risk = "MEDIUM"
        decision = "MANUAL_REVIEW"
        confidence = 0.75
    else:
        risk = "LOW"
        decision = "ACCEPT"
        confidence = 0.85

    return {
        "analysis": {
            "fraud_score": fraud_score,
            "risk_level": risk,
            "decision": decision,
            "confidence": confidence
        },
        "verification": {
            "github": github_result,
            "linkedin": {
                "found": linkedin_valid,
                "valid": linkedin_valid
            },
            "contact_info": contact_info
        },
        "flags": flags
    }