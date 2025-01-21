from fastapi import APIRouter, Depends, HTTPException
from app.database import db
from app.schemas import TransferResponse, Transfer
from datetime import datetime
from app.utils.security import get_current_user
from typing import List
from bson import ObjectId

router = APIRouter()

@router.get("/", response_model=List[TransferResponse])
async def get_transfers(current_user: dict = Depends(get_current_user)):
    """
    Obtiene las transferencias asociadas a la empresa actual.
    """
    company_id = current_user["company_id"]
    transfers = await db.transfers.find({"company_id": company_id}).to_list(length=100)
    return transfers


@router.get("/{transfer_id}", response_model=Transfer)
async def get_transfer_details(
    transfer_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene los detalles de una transferencia específica por su ID (campo 'id')
    y que pertenezca a la empresa del usuario autenticado.
    """
    transfer_doc = await db.transfers.find_one({
        "id": transfer_id,
        "company_id": current_user["company_id"] 
    })

    if not transfer_doc:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró la transferencia con el ID {transfer_id}"
        )

    # Asegúrate de que el campo 'timestamp' sea un datetime al construir el modelo
    if isinstance(transfer_doc.get("timestamp"), str):
        transfer_doc["timestamp"] = datetime.fromisoformat(transfer_doc["timestamp"])

    # Convertimos el documento a la clase Pydantic Transfer.
    # Retornará todos los campos definidos en el esquema Transfer.
    return Transfer(**transfer_doc)
