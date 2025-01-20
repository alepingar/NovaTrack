from pydantic import BaseModel, EmailStr , HttpUrl , validator
from typing import Optional
from datetime import datetime
from pydantic_settings import BaseSettings

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    password: str
    
class CompanyCreate(BaseModel):
    name: str  # Nombre de la empresa
    email: EmailStr  # Correo principal de contacto
    password: str  # Contraseña de la cuenta
    confirm_password: str

    @validator("confirm_password")
    def passwords_match(cls, confirm_password, values):
        password = values.get("password")
        if password != confirm_password:
            raise ValueError("Las contraseñas no coinciden")
        return confirm_password
    
    industry: Optional[str] = None  # Sector industrial (opcional)
    role: str = "admin"  # Rol predeterminado (admin)
    country: str  # País de la empresa
    phone_number: Optional[str] = None  # Teléfono de contacto
    tax_id: Optional[str] = None  # Número de identificación fiscal (CIF, NIF, etc.)
    website: Optional[HttpUrl] = None  # Página web de la empresa
    description: Optional[str] = None  # Descripción breve de la empresa
    address: Optional[str] = None  # Dirección física de la empresa
    founded_date: Optional[datetime] = None  # Fecha de fundación de la empresa
    profileImage: Optional[str] = None  # URL del logo de la empresa

class CompanyResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    industry: Optional[str] = None
    role: str = "admin"
    country: str
    phone_number: Optional[str] = None
    tax_id: Optional[str] = None
    website: Optional[HttpUrl] = None
    description: Optional[str] = None
    address: Optional[str] = None
    founded_date: Optional[datetime] = None
    profileImage: Optional[str] = None
    created_at: datetime  # Fecha de creación del registro
    updated_at: datetime  # Última fecha de actualización del perfil

class UpdateCompanyProfile(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    industry: Optional[str]
    country: Optional[str]
    phone_number: Optional[str]
    tax_id: Optional[str]
    website: Optional[HttpUrl]
    description: Optional[str]
    address: Optional[str]
    founded_date: Optional[datetime]
    profileImage: Optional[str]

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    name: str
    surname: str
    email: EmailStr
    role: str

class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str
    role: str

class UserUpdate(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    email: Optional[EmailStr]
    role: Optional[str]



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



class Settings(BaseSettings):
    email_host: str
    email_port: int
    email_user: str
    email_password: str
    email_from: str
    email_name: str

    class Config:
        env_file = ".env"

settings = Settings()