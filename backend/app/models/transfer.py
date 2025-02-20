from pydantic import BaseModel,  Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# Transfer Schemas
class Transfer(BaseModel): 
    id: UUID  # ID único de la transferencia
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
    status: str = Field(..., pattern=r"^(pendiente|completeda|fallida)$", description="Estado: pending, completed o failed")
    user_identifier: Optional[str] = Field(None, description="Identificador del usuario que realiza la transacción (e.g., email, ID externo)")
    is_recurring: Optional[bool] = False  # Indica si es una transferencia recurrente
    device_fingerprint: Optional[str] = Field(None, max_length=500, description="Identificador único del dispositivo usado")
    client_ip: Optional[str] = Field(None, pattern=r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", description="Dirección IP del cliente")
    company_id: str = Field(..., description="ID de la empresa propietaria de la transacción")
    transaction_fee: Optional[float] = Field(0, description="Tarifa aplicada a la transacción (si existe)")
    is_anomalous: Optional[bool] = False  # Indica si se detectó como anómala
    linked_order_id: Optional[str] = Field(None, description="ID de la orden asociada (si aplica)")

class TransferResponse(BaseModel):
    id: UUID
    amount: float
    from_account: str
    to_account: str
    timestamp: datetime
    status: str
    is_anomalous: Optional[bool] = False
    description: Optional[str] = None
    currency: Optional[str] = "EUR"