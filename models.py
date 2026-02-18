# models.py
from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

class Report(BaseModel):
    filename: str
    uploaded_by: str
