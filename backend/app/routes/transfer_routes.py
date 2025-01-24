from fastapi import APIRouter, Depends, HTTPException , Query
from app.utils.security import get_current_user
from app.services.transfer_services import (
    fetch_transfers,
    fetch_transfer_details,
    fetch_summary,
)
from app.schemas import TransferResponse, Transfer
from typing import List
from typing import Dict, Union
from app.database import db


router = APIRouter()

@router.get("/", response_model=List[TransferResponse])
async def get_transfers(current_user: dict = Depends(get_current_user)):
    """
    Obtiene las transferencias asociadas a la empresa actual.
    """
    company_id = current_user["company_id"]
    return await fetch_transfers(company_id)


@router.get("/summary-data", response_model=Dict[str, Union[int, float]])
async def get_summary_data(current_user: dict = Depends(get_current_user)):
    """
    Devuelve un resumen de las transferencias asociadas a la empresa actual.
    """
    try:
        company_id = current_user["company_id"]
        return await fetch_summary(company_id)
    except Exception as e:
        print(f"Error al obtener el resumen: {e}")
        raise HTTPException(status_code=500, detail="Error al generar el resumen")



@router.get("/{transfer_id}", response_model=Transfer)
async def get_transfer_details(transfer_id: int, current_user: dict = Depends(get_current_user)):
    """
    Obtiene los detalles de una transferencia específica por su ID.
    """
    company_id = current_user["company_id"]
    return await fetch_transfer_details(company_id, transfer_id)


