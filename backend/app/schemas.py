from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator
from typing import Optional
from datetime import datetime
from pydantic_settings import BaseSettings

# Login Schema
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=50, description="La contraseña debe tener entre 8 y 50 caracteres")

# Password Reset Schemas
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    password: str = Field(..., min_length=8, max_length=50, description="La nueva contraseña debe tener entre 8 y 50 caracteres")

# Company Schemas
class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=40, description="El nombre debe tener entre 2 y 40 caracteres")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=50, description="La contraseña debe tener entre 8 y 50 caracteres")
    confirm_password: str

    @validator("confirm_password")
    def passwords_match(cls, confirm_password, values):
        password = values.get("password")
        if password != confirm_password:
            raise ValueError("Las contraseñas no coinciden")
        return confirm_password

    industry: Optional[str] = Field(None, max_length=50, description="El sector industrial no debe superar los 50 caracteres")
    role: str = "admin"
    country: str = Field(..., min_length=2, max_length=50, description="El país debe tener entre 2 y 50 caracteres")
    phone_number: Optional[str] = Field(
        None, pattern=r"^\+?[1-9]\d{1,14}$", description="El número de teléfono debe seguir el formato internacional (E.164)"
    )
    tax_id: Optional[str] = Field(None, min_length=8, max_length=15, description="El ID fiscal debe tener entre 8 y 15 caracteres")
    website: Optional[HttpUrl]
    description: Optional[str] = Field(None, max_length=500, description="La descripción no debe superar los 500 caracteres")
    address: Optional[str] = Field(None, max_length=200, description="La dirección no debe superar los 200 caracteres")
    founded_date: Optional[datetime]

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
    created_at: datetime
    updated_at: datetime

class UpdateCompanyProfile(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=40)
    email: Optional[EmailStr]
    industry: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, min_length=2, max_length=50)
    phone_number: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    tax_id: Optional[str] = Field(None, min_length=8, max_length=15)
    website: Optional[HttpUrl]
    description: Optional[str] = Field(None, max_length=500)
    address: Optional[str] = Field(None, max_length=200)
    founded_date: Optional[datetime]

# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str

# User Schemas
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

# Transfer Schemas
class Transfer(BaseModel):
    id: int  # ID único de la transferencia
    amount: float = Field(..., gt=0, description="El monto debe ser mayor a 0")
    currency: str = Field(..., min_length=3, max_length=3, description="El código de moneda debe cumplir ISO 4217")
    from_account: str = Field(..., min_length=10, max_length=20, description="Número de cuenta del remitente (10-20 caracteres)")
    to_account: str = Field(..., min_length=10, max_length=20, description="Número de cuenta del receptor (10-20 caracteres)")
    timestamp: datetime  # Marca de tiempo de la transferencia
    description: Optional[str] = Field(None, max_length=500)  # Descripción de la transferencia
    category: Optional[str] = Field(None, max_length=50)  # Categoría de la transacción (e.g., compras, servicios)
    origin_location: Optional[str] = Field(None, max_length=100)  # Ubicación de origen (ciudad, país)
    destination_location: Optional[str] = Field(None, max_length=100)  # Ubicación de destino
    payment_method: Optional[str] = Field(None, max_length=50)  # Método de pago (e.g., tarjeta, transferencia)
    status: str = Field(..., pattern=r"^(pending|completed|failed)$", description="Estado: pending, completed o failed")
    user_identifier: Optional[str] = Field(None, description="Identificador del usuario que realiza la transacción (e.g., email, ID externo)")
    is_recurring: Optional[bool] = False  # Indica si es una transferencia recurrente
    device_fingerprint: Optional[str] = Field(None, max_length=500, description="Identificador único del dispositivo usado")
    client_ip: Optional[str] = Field(None, pattern=r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", description="Dirección IP del cliente")
    company_id: str = Field(..., description="ID de la empresa propietaria de la transacción")
    transaction_fee: Optional[float] = Field(0, description="Tarifa aplicada a la transacción (si existe)")
    is_anomalous: Optional[bool] = False  # Indica si se detectó como anómala
    linked_order_id: Optional[str] = Field(None, description="ID de la orden asociada (si aplica)")

class TransferResponse(BaseModel):
    id: int
    amount: float
    from_account: str
    to_account: str
    timestamp: datetime
    status: str
    is_anomalous: Optional[bool] = False
    description: Optional[str] = None


# Settings Schema
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
