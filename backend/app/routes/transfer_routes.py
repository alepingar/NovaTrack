from fastapi import APIRouter, Depends
from app.utils.security import get_current_user
from app.services.transfer_services import (
    fetch_transfers,
    fetch_transfer_details,
    fetch_summary,
    fetch_anomalies,
)
from app.schemas import TransferResponse, Transfer
from typing import List

router = APIRouter()

@router.get("/", response_model=List[TransferResponse])
async def get_transfers(current_user: dict = Depends(get_current_user)):
    """
    Obtiene las transferencias asociadas a la empresa actual.
    """
    company_id = current_user["company_id"]
    return await fetch_transfers(company_id)

@router.get("/{transfer_id}", response_model=Transfer)
async def get_transfer_details(transfer_id: int, current_user: dict = Depends(get_current_user)):
    """
    Obtiene los detalles de una transferencia específica por su ID.
    """
    company_id = current_user["company_id"]
    return await fetch_transfer_details(company_id, transfer_id)

@router.get("/summary")
async def get_summary(current_user: dict = Depends(get_current_user)):
    """
    Genera un resumen de las transferencias.
    """
    company_id = current_user["company_id"]
    return await fetch_summary(company_id)

@router.get("/anomalies", response_model=List[TransferResponse])
async def get_anomalies(current_user: dict = Depends(get_current_user)):
    """
    Obtiene las anomalías más recientes.
    """
    company_id = current_user["company_id"]
    return await fetch_anomalies(company_id)
