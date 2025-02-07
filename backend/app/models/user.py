from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    id: str
    name: str
    surname: str
    email: EmailStr
    role: str

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=30, description="El nombre debe tener entre 2 y 30 caracteres")
    surname: str = Field(..., min_length=2, max_length=30, description="El apellido debe tener entre 2 y 30 caracteres")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=50, description="La contraseña debe tener entre 8 y 50 caracteres")
    role: str = Field(..., pattern=r"^(staff|manager)$", description="El rol debe ser 'staff' o 'manager'")

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=30)
    surname: Optional[str] = Field(None, min_length=2, max_length=30)
    email: Optional[EmailStr]
    role: Optional[str] = Field(None, pattern=r"^(staff|manager)$")