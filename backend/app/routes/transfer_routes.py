from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from app.utils.security import get_current_user
from app.services.transfer_services import (
    fetch_transfers,
    fetch_transfer_details,
    fetch_summary,
    fetch_anomalous_volume_by_day,
    fetch_status_distribution,
    fetch_volume_by_day,
    fetch_public_summary_data,
    fetch_total_amount_per_month,
    fetch_summary_data_per_month_for_company,
    fetch_new_users_per_month,
    fetch_total_amount_per_month_for_company,
    fetch_transfers_by_range,
    fetch_number_anomaly_transfers_per_period,
    fetch_number_transfers_per_period
)
from app.models.transfer import TransferResponse, Transfer
from typing import List
from typing import Dict, Union
from app.database import db
from uuid import UUID
from app.isolation_forest.upload_files import upload_camt_file

router = APIRouter()

@router.get("/", response_model=List[TransferResponse])
async def get_transfers(current_user: dict = Depends(get_current_user)):
    """
    Obtiene las transferencias asociadas a la empresa actual.
    """
    company_id = current_user["company_id"]
    return await fetch_transfers(company_id)

@router.get("/per-month/{year}/{month}", response_model=int)
async def get_transfers_per_month(year: int, month: int, period: str = Query("3months", enum=["month", "3months", "year"])):
    return await fetch_number_transfers_per_period(year, month, period)

@router.get("/anomaly/per-month/{year}/{month}", response_model=int)
async def get_anomaly_transfers_per_month(year: int, month: int, period: str = Query("3months", enum=["month", "3months", "year"])):
    return await fetch_number_anomaly_transfers_per_period(year, month, period)

@router.get("/amount/per-month/{year}/{month}", response_model=float)
async def get_amount_transfers_per_month(year: int, month: int):
    """
    Obtiene las transferencias asociadas a la empresa actual para un mes específico.
    """
    amount_count = await fetch_total_amount_per_month(year, month)
    return amount_count

@router.get("/amount/company/per-month/{year}/{month}", response_model=float)
async def get_amount_transfers_per_month_by_company(year: int, month: int,
    current_user: dict = Depends(get_current_user)):
    """
    Obtiene las transferencias asociadas a la empresa actual para un mes específico.
    """
    amount_count = await fetch_total_amount_per_month_for_company(current_user["company_id"], year, month)
    return amount_count

@router.get("/summary/per-month/{year}/{month}", response_model=dict)
async def get_summary_for_company(
    year: int,
    month: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene un resumen de las transferencias para la empresa actual en un mes y año determinados.
    """
    company_id = current_user["company_id"]
    summary_data = await fetch_summary_data_per_month_for_company(company_id, year, month)
    return summary_data

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
async def get_volume_by_day(
    current_user: dict = Depends(get_current_user),
    period: str = Query("3months", enum=["month", "3months", "year"]),
):
    try:
        company_id = current_user["company_id"]
        return await fetch_volume_by_day(company_id, period)
    except Exception as e:
        print(f"Error al obtener el volumen por día: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar el volumen por día")


@router.get("/anomalous/volume-by-day")
async def get_anomaous_volume_by_day(
    current_user: dict = Depends(get_current_user),
    period: str = Query("3months", enum=["month", "3months", "year"]),
):
    try:
        company_id = current_user["company_id"]
        return await fetch_anomalous_volume_by_day(company_id, period)
    except Exception as e:
        print(f"Error al obtener el volumen anomalo por día: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar el volumen anomalo por día")


@router.get("/status-distribution")
async def get_status_distribution(
    current_user: dict = Depends(get_current_user),
    period: str = Query("3months", enum=["month", "3months", "year"]),
):
    try:
        company_id = current_user["company_id"]
        return await fetch_status_distribution(company_id, period)
    except Exception as e:
        print(f"Error al obtener la distribución de estados: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar la distribución de estados")

@router.get("/{transfer_id}", response_model=Transfer)
async def get_transfer_details(transfer_id: UUID, current_user: dict = Depends(get_current_user)):
    """
    Obtiene los detalles de una transferencia específica por su ID.
    """
    company_id = current_user["company_id"]
    return await fetch_transfer_details(company_id, transfer_id)


@router.get("/new-users/per-month/{year}/{month}", response_model=int)
async def get_new_users_per_month(year: int, month: int,  current_user: dict = Depends(get_current_user)):
    """
    Obtiene la cantidad de usuarios nuevos del mes que nos encontramos.
    """
    company_id = current_user["company_id"]
    return await fetch_new_users_per_month(company_id, year, month)  

@router.get("/filter/range", response_model=List[TransferResponse])
async def get_transfers_by_range(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene las transferencias dentro de un rango de fechas específico.
    """
    company_id = current_user["company_id"]
    return await fetch_transfers_by_range(company_id, start_date, end_date)

@router.get("/filter/all", response_model=List[TransferResponse])
async def get_all_transfers(current_user: dict = Depends(get_current_user)):
    """
    Obtiene todas las transferencias.
    """
    company_id = current_user["company_id"]
    return await fetch_transfers(company_id)

@router.post("/upload-camt")
async def upload_camt(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """
    Endpoint para subir archivos CAMT.053 y procesarlos.
    """
    return await upload_camt_file(file, current_user["company_id"])