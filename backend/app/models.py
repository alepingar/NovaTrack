from pydantic import BaseModel, EmailStr
from typing import Optional


class Company(BaseModel):
    id: Optional[str]
    name: str
    email: EmailStr
    password: str
    industry: Optional[str] = None
    role: str = "admin"