from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
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


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    company_id: str
    role: str = "staff" 

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
    company_id: str