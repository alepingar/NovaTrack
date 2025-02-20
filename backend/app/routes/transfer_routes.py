from fastapi import APIRouter, Depends, HTTPException
from app.utils.security import get_current_user
from app.services.transfer_services import (
    fetch_transfers,
    fetch_transfer_details,
    fetch_summary,
    fetch_amount_by_category,
    fetch_status_distribution,
    fetch_top_origin_locations,
    fetch_volume_by_day,
    fetch_public_summary_data
)
from app.models.transfer import TransferResponse, Transfer
from typing import List
from typing import Dict, Union
from app.database import db
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[TransferResponse])
async def get_transfers(current_user: dict = Depends(get_current_user)):
    """
    Obtiene las transferencias asociadas a la empresa actual.
    """
    company_id = current_user["company_id"]
    return await fetch_transfers(company_id)



@router.get("/public/summary-data", response_model=Dict[str, Union[int, float]])
async def get_public_summary_data():
    """
    Devuelve un resumen de todas las transferencias
    """
    try:
        return await fetch_public_summary_data()
    except Exception as e:
        print(f"Error al obtener el resumen: {e}")
        raise HTTPException(status_code=500, detail="Error al generar el resumen")

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
    

@router.get("/volume-by-day")
async def get_volume_by_day(current_user: dict = Depends(get_current_user)):
    try:
        company_id = current_user["company_id"]
        return await fetch_volume_by_day(company_id)
    except Exception as e:
        print(f"Error al obtener el volumen por día: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar el volumen por día")


@router.get("/amount-by-category")
async def get_amount_by_category(current_user: dict = Depends(get_current_user)):
    try:
        company_id = current_user["company_id"]
        return await fetch_amount_by_category(company_id)
    except Exception as e:
        print(f"Error al obtener los montos por categoría: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar los montos por categoría")


@router.get("/status-distribution")
async def get_status_distribution(current_user: dict = Depends(get_current_user)):
    try:
        company_id = current_user["company_id"]
        return await fetch_status_distribution(company_id)
    except Exception as e:
        print(f"Error al obtener la distribución de estados: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar la distribución de estados")


@router.get("/top-origin-locations")
async def get_top_origin_locations(current_user: dict = Depends(get_current_user)):
    try:
        company_id = current_user["company_id"]
        return await fetch_top_origin_locations(company_id)
    except Exception as e:
        print(f"Error al obtener las ubicaciones de origen más comunes: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar las ubicaciones de origen")




@router.get("/{transfer_id}", response_model=Transfer)
async def get_transfer_details(transfer_id: UUID, current_user: dict = Depends(get_current_user)):
    """
    Obtiene los detalles de una transferencia específica por su ID.
    """
    company_id = current_user["company_id"]
    return await fetch_transfer_details(company_id, transfer_id)


