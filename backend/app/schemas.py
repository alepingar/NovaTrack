from pydantic import BaseModel, EmailStr
from typing import Optional

class CompanyCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    industry: Optional[str] = None


class CompanyLogin(BaseModel):
    email: EmailStr
    password: str


class CompanyResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    industry: Optional[str] = None
    role: str = "admin"

class Token(BaseModel):
    access_token: str
    token_type: str