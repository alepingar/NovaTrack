from datetime import datetime
from logging import log
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from app.utils.security import get_current_user
from app.services.transfer_services import (
    fetch_transfers,
    fetch_transfer_details,
    fetch_public_summary_data,
    fetch_total_amount_per_month,
    fetch_summary_data_per_month_for_company,
    fetch_number_anomaly_transfers_per_period,
    fetch_number_transfers_per_period,
    get_transfer_stats_by_company,
    fetch_dashboard_data_internal,
)
from app.models.transfer import TransferResponse, Transfer
from typing import Any, List, Optional
from typing import Dict, Union
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

@router.get("/dashboard-data", response_model=Dict[str, Any])
async def get_dashboard_data(
    start_date: Optional[datetime] = Query(None, description="ISO Format Start Date"),
    end_date: Optional[datetime] = Query(None, description="ISO Format End Date"),
    bank_prefix: Optional[str] = Query(None, description="4-digit bank code"),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Endpoint unificado para obtener todos los datos del dashboard,
    aplicando filtros opcionales. Devuelve datos globales si no hay filtros.
    """
    try:
        company_id = current_user["company_id"]
        # Llama a la función interna refactorizada
        dashboard_data = await fetch_dashboard_data_internal(
            company_id, start_date, end_date, bank_prefix, min_amount, max_amount
        )
        return dashboard_data
    except Exception as e:
        # Loggear el error que pudo haber sido re-lanzado desde la función interna
        log.error(f"API Error fetching dashboard data: {e}", exc_info=True)
        # Devolver un error HTTP 500 genérico
        raise HTTPException(status_code=500, detail=f"Error processing dashboard data.")

@router.get("/stats", response_model=Dict[str, Any])
async def get_company_stats(current_user: dict = Depends(get_current_user)):
    company_id = current_user["company_id"]
    if not company_id:
        raise HTTPException(status_code=400, detail="Company ID is missing")
    return await get_transfer_stats_by_company(company_id)


@router.get("/per-month/{year}/{month}", response_model=int)
async def get_transfers_per_month(year: int, month: int, period: str = Query("3months", enum=["month", "3months", "year"])):
    return await fetch_number_transfers_per_period(year, month, period)

@router.get("/anomaly/per-month/{year}/{month}", response_model=int)
async def get_anomaly_transfers_per_month(year: int, month: int, period: str = Query("3months", enum=["month", "3months", "year"])):
    return await fetch_number_anomaly_transfers_per_period(year, month, period)

@router.get("/amount/per-month/{year}/{month}", response_model=float)
async def get_amount_transfers_per_month(year: int, month: int, period: str = Query("3months", enum=["month", "3months", "year"])):
    """
#     Obtiene las transferencias asociadas a la empresa actual para un mes específico.
#     """
    amount_count = await fetch_total_amount_per_month(year, month, period)
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
        print(f"Error al obtener el resumen público: {e}")
        raise HTTPException(status_code=500, detail="Error al generar el resumen público")


@router.post("/upload-camt")
async def upload_camt(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """
    Endpoint para subir archivos CAMT.053 y procesarlos.
    """
    return await upload_camt_file(file, current_user["company_id"])


@router.get("/{transfer_id}", response_model=Transfer)
async def get_transfer_details(transfer_id: UUID, current_user: dict = Depends(get_current_user)):
    """
    Obtiene los detalles de una transferencia específica por su ID.
    """
    company_id = current_user["company_id"]
    return await fetch_transfer_details(company_id, transfer_id)