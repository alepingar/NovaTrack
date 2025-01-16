from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class CompanyCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    industry: Optional[str] = None
    role: str = "admin"

class CompanyResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    industry: Optional[str] = None
    role: str = "admin"

class UpdateCompanyProfile(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    industry: Optional[str]

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str


class Transfer(BaseModel):
    id: int
    amount: float
    currency: str
    from_account: str
    to_account: str
    timestamp: datetime
    description: Optional[str] = None
    category: Optional[str] = None
    origin_location: Optional[str] = None
    destination_location: Optional[str] = None
    payment_method: Optional[str] = None
    status: str
    user_id: Optional[str] = None
    recurring: Optional[bool] = False
    client_ip: Optional[str] = None
    company_id: str
    is_anomalous: Optional[bool] = False

class TransferResponse(BaseModel):
    id: int
    amount: float
    from_account: str
    to_account: str
    timestamp: datetime
    is_anomalous: Optional[bool] = False