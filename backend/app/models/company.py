from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator
from typing import Dict, List, Optional
from datetime import datetime
import re
from enum import Enum
class SubscriptionPlan(str, Enum):
    BASICO = "BASICO"
    PRO = "PRO"
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
    industry: Optional[str] = Field(None, max_length=50, description="El sector industrial no debe superar los 50 caracteres")
    country: str = Field(..., min_length=2, max_length=30, description="El país debe tener entre 2 y 30 caracteres")
    phone_number: Optional[str] = Field(
        None, pattern=r"^\+?[1-9]\d{1,14}$", description="El número de teléfono debe seguir el formato internacional (E.164)"
    )
    tax_id: Optional[str] = Field(None, min_length=8, max_length=15, description="El ID fiscal debe tener entre 8 y 15 caracteres")
    address: Optional[str] = Field(None, max_length=100, description="La dirección no debe superar los 200 caracteres")
    founded_date: Optional[datetime]
    billing_account_number: str = Field(..., description="Número de cuenta bancaria de la empresa para recibir pagos")
    entity_type: EntityType = Field(..., description="Tipo de entidad legal de la empresa")
    subscription_plan: SubscriptionPlan = SubscriptionPlan.BASICO
    # Consentimiento y Regulación
    terms_accepted: bool
    privacy_policy_accepted: bool
    data_processing_consent: bool
    communication_consent: bool = False
    consent_timestamp: datetime = Field(default_factory=datetime.utcnow)
    uploads_count: int = 0
    
    # Seguridad y Auditoría
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked: bool = False
    
    # Trazabilidad y Cumplimiento
    gdpr_request_log: List[Dict[str, str]] = Field(default_factory=list)
  # Lista de acciones GDPR (ej. solicitudes de acceso/eliminación)
    account_deletion_requested: bool = False
    data_sharing_consent: bool = False

    @validator("confirm_password")
    def passwords_match(cls, confirm_password, values):
        password = values.get("password")
        if password != confirm_password:
            raise ValueError("Las contraseñas no coinciden")
        return confirm_password

    @validator("billing_account_number")
    def validate_billing_account_number(cls, value):
        iban_pattern = r"^ES\d{2}\d{4}\d{4}\d{12}$"
        if not re.match(iban_pattern, value):
            raise ValueError("El número de cuenta debe ser un IBAN español válido")
        return value
    
    @validator("email")
    def normalize_email(cls, value):
        return value.lower()

class CompanyResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    industry: Optional[str] = None
    country: str
    phone_number: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None
    founded_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    billing_account_number: Optional[str] = None
    subscription_plan: Optional[SubscriptionPlan] = None
    

class UpdateCompanyProfile(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=40)
    email: Optional[EmailStr]
    industry: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, min_length=2, max_length=50)
    phone_number: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    tax_id: Optional[str] = Field(None, min_length=8, max_length=15)
    address: Optional[str] = Field(None, max_length=200)
    founded_date: Optional[datetime]


class ConsentUpdate(BaseModel):
    consent: bool

class CompanyGDPRRequest(BaseModel):
    action: str = Field(..., description="Acción GDPR solicitada (ej. 'acceso', 'eliminación')")
