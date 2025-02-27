from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

# Modelo de Transferencia basado en camt.053
class Transfer(BaseModel):
    id: UUID  # ID único de la transferencia (camt.053)
    amount: float = Field(..., gt=0, description="Monto de la transacción (camt.053)")
    currency: str = Field(..., min_length=3, max_length=3, description="Moneda de la transacción (camt.053)")
    from_account: str = Field(..., min_length=10, max_length=20, description="Número de cuenta del remitente (camt.053)")
    to_account: str = Field(..., min_length=10, max_length=20, description="Número de cuenta del destinatario (camt.053)")
    timestamp: datetime  # Fecha y hora de la transacción (camt.053)
    status: str = Field(..., pattern=r"^(pendiente|completada|fallida)$", description="Estado de la transacción (camt.053)")
    company_id: str = Field(..., description="ID de la empresa propietaria de la transacción")
    message_identifier: Optional[str] = Field(None, max_length=35, description="Identificador del mensaje del extracto bancario (camt.053)")
    is_anomalous: Optional[bool] = False  # Indicador para anomalías
    reference: Optional[str] = Field(None, max_length=100, description="Referencia o identificador adicional de la transacción (camt.053)")

class TransferResponse(BaseModel):
    id: UUID
    amount: float
    from_account: str
    to_account: str
    timestamp: datetime
    status: str
    is_anomalous: Optional[bool] = False
    message_identifier: Optional[str] = None
    reference: Optional[str] = None
    currency: Optional[str] = "EUR"