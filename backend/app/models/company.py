from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator
from typing import Optional
from datetime import datetime
import re
from enum import Enum

class EntityType(str, Enum):
    SA = "Sociedad Anónima"
    SL = "Sociedad Limitada"
    SLNE = "Sociedad Limitada Nueva Empresa"
    AUTONOMO = "Autónomo"
    COOPERATIVA = "Sociedad Cooperativa"
    SOCIEDAD_CIVIL = "Sociedad Civil"
    COMUNIDAD_BIENES = "Comunidad de Bienes"
    ENTIDAD_PUBLICA = "Entidad Pública"
    ASOCIACION = "Asociación"
    FUNDACION = "Fundación"
    OTRO = "Otro"

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
    @validator('founded_date')
    def validate_founded_date(cls, value):
        today = datetime.today()
        if value > today:
            raise ValueError("La fecha de fundación no puede ser futura.")
        
        if value.year < 1800:
            raise ValueError("La fecha de fundación no puede ser anterior a 1800.")
        
        return value
    billing_account_number: str = Field(..., description="Número de cuenta bancaria de la empresa para recibir pagos")
    entity_type: EntityType = Field(..., description="Tipo de entidad legal de la empresa")

    @validator("billing_account_number")
    def validate_billing_account_number(cls, value):
        # Expresión regular para validar un IBAN español
        iban_pattern = r"^ES\d{2}\d{4}\d{4}\d{2}\d{10}$"
        if not re.match(iban_pattern, value):
            raise ValueError("El número de cuenta debe ser un IBAN español válido")
        return value
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
    billing_account_number: Optional[str] = None

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