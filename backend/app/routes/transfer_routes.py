from datetime import datetime
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
    fetch_new_senders,  # Renombramos para mayor claridad
    fetch_transfers_by_filters, # Usaremos esta para el rango de fechas y otros filtros
    fetch_number_anomaly_transfers_per_period,
    fetch_number_transfers_per_period,
    get_transfer_stats_by_company,
    fetch_amount_by_month # Nuevo método para el gráfico de montos
)
from app.models.transfer import TransferResponse, Transfer
from typing import Any, List
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

@router.get("/amount/company/per-month/{year}/{month}", response_model=float)
async def get_amount_transfers_per_month_by_company(year: int, month: int,
    current_user: dict = Depends(get_current_user)):
    """
    Obtiene el monto total de transferencias de la compañía actual para un mes específico.
    """
    amount_count = await fetch_amount_by_month(current_user["company_id"], year, month)
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

@router.get("/summary-data", response_model=Dict[str, Union[int, float]])
async def get_summary_data(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    bank_prefix: str = Query(None),
    min_amount: float = Query(None),
    max_amount: float = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Devuelve un resumen de las transferencias asociadas a la empresa actual, con filtros opcionales.
    """
    try:
        company_id = current_user["company_id"]
        return await fetch_summary(company_id, start_date, end_date, bank_prefix, min_amount, max_amount)
    except Exception as e:
        print(f"Error al obtener el resumen filtrado: {e}")
        raise HTTPException(status_code=500, detail="Error al generar el resumen filtrado")

@router.get("/volume-by-day")
async def get_volume_by_day(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    bank_prefix: str = Query(None),
    min_amount: float = Query(None),
    max_amount: float = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtiene el volumen de transferencias por día, con filtros opcionales.
    """
    try:
        company_id = current_user["company_id"]
        return await fetch_volume_by_day(company_id, start_date, end_date, bank_prefix, min_amount, max_amount)
    except Exception as e:
        print(f"Error al obtener el volumen por día filtrado: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar el volumen por día filtrado")

@router.get("/anomalous/volume-by-day")
async def get_anomaous_volume_by_day(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    bank_prefix: str = Query(None),
    min_amount: float = Query(None),
    max_amount: float = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtiene el volumen de transferencias anómalas por día, con filtros opcionales.
    """
    try:
        company_id = current_user["company_id"]
        return await fetch_anomalous_volume_by_day(company_id, start_date, end_date, bank_prefix, min_amount, max_amount)
    except Exception as e:
        print(f"Error al obtener el volumen anómalo por día filtrado: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar el volumen anómalo por día filtrado")

@router.get("/status-distribution")
async def get_status_distribution(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    bank_prefix: str = Query(None),
    min_amount: float = Query(None),
    max_amount: float = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Obtiene la distribución de estados de las transferencias, con filtros opcionales.
    """
    try:
        company_id = current_user["company_id"]
        return await fetch_status_distribution(company_id, start_date, end_date, bank_prefix, min_amount, max_amount)
    except Exception as e:
        print(f"Error al obtener la distribución de estados filtrada: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar la distribución de estados filtrada")

@router.get("/new-senders", response_model=int)
async def get_new_senders_filtered(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    bank_prefix: str = Query(None),
    min_amount: float = Query(None),
    max_amount: float = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene el número de remitentes únicos dentro del rango de fechas especificado y otros filtros.
    """
    company_id = current_user["company_id"]
    return await fetch_new_senders(company_id, start_date, end_date, bank_prefix, min_amount, max_amount)

# Eliminamos la ruta anterior que era específica para el mes actual
# @router.get("/new-users/per-month/{year}/{month}", response_model=int)
# async def get_new_users_per_month(year: int, month: int,   current_user: dict = Depends(get_current_user)):
#     """
#     Obtiene la cantidad de usuarios nuevos del mes que nos encontramos.
#     """
#     company_id = current_user["company_id"]
#     return await fetch_new_users_per_month(company_id, year, month)

# Esta ruta ahora es más general y se llama get_transfers_filtered
@router.get("/filter", response_model=List[TransferResponse])
async def get_transfers_filtered(
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    bank_prefix: str = Query(None),
    min_amount: float = Query(None),
    max_amount: float = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene las transferencias aplicando filtros opcionales.
    """
    company_id = current_user["company_id"]
    return await fetch_transfers_by_filters(company_id, start_date, end_date, bank_prefix, min_amount, max_amount)

# La ruta específica por rango de fechas ya no es necesaria, se usa la de "/filter"
# @router.get("/filter/range", response_model=List[TransferResponse])
# async def get_transfers_by_range(
#     start_date: datetime = Query(...),
#     end_date: datetime = Query(...),
#     current_user: dict = Depends(get_current_user)
# ):
#     """
#     Obtiene las transferencias dentro de un rango de fechas específico.
#     """
#     company_id = current_user["company_id"]
#     return await fetch_transfers_by_range(company_id, start_date, end_date)

# La ruta para obtener todas las transferencias sin filtros ya existe en "/"

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