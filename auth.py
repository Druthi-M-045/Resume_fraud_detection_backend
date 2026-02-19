# auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import users
from models import UserLogin
from utils import create_token, decode_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Signup route (only for new users, admin must be pre-defined)
@router.post("/signup")
def signup(data: UserLogin):
    # Check if username already exists
    existing_user = next((u for u in users if u["username"] == data.username), None)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Add new user with role 'user'
    new_user = {"username": data.username, "password": data.password, "role": "user"}
    users.append(new_user)
    token = create_token(new_user)
    return {"message": "User created successfully", "access_token": token, "role": "user"}

# Login route
@router.post("/login")
def login(data: OAuth2PasswordRequestForm = Depends()):
    user = next((u for u in users if u["username"] == data.username and u["password"] == data.password), None)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(user)
    return {"access_token": token, "token_type": "bearer", "role": user["role"]}

# Dependency to get current user from JWT
def get_current_user(token: str = Depends(oauth2_scheme)):
    return decode_token(token)
