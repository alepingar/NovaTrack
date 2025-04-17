import pandas as pd
from app.database import db
from app.models.transfer import Transfer, TransferResponse
from datetime import datetime, timezone, timedelta
from typing import Any, List
from fastapi import HTTPException, Query
from typing import Dict, Union
from uuid import UUID
from pymongo import ASCENDING

async def fetch_transfers(company_id: str) -> List[TransferResponse]:
    """
    Fetch all transfers for a given company.
    """
    transfers = await db.transfers.find({"company_id": company_id}).to_list()
    return transfers

async def fetch_number_transfers_per_period(year: int, month: int, period: str = "3months") -> int:
    end_date = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc) + timedelta(days=32)
    end_date = end_date.replace(day=1) - timedelta(seconds=1)

    if period == "month":
        start_date = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
    elif period == "year":
        start_date = datetime(year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    else:  # 3months
        start_month = month - 2 if month > 2 else (month - 2) + 12
        start_year = year if month > 2 else year - 1
        start_date = datetime(start_year, start_month, 1, 0, 0, 0, tzinfo=timezone.utc)

    pipeline = [
        {"$match": {"timestamp": {"$gte": start_date, "$lte": end_date}}},
        {"$count": "count"}
    ]

    result = await db.transfers.aggregate(pipeline).to_list(length=None)
    return result[0]["count"] if result else 0

async def fetch_number_anomaly_transfers_per_period(year: int, month: int, period: str = "3months") -> int:
    end_date = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc) + timedelta(days=32)
    end_date = end_date.replace(day=1) - timedelta(seconds=1)

    if period == "month":
        start_date = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
    elif period == "year":
        start_date = datetime(year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    else:  # 3months
        start_month = month - 2 if month > 2 else (month - 2) + 12
        start_year = year if month > 2 else year - 1
        start_date = datetime(start_year, start_month, 1, 0, 0, 0, tzinfo=timezone.utc)

    pipeline = [
        {"$match": {"timestamp": {"$gte": start_date, "$lte": end_date}, "is_anomalous": True}},
        {"$count": "count"}
    ]

    result = await db.transfers.aggregate(pipeline).to_list(length=None)
    return result[0]["count"] if result else 0

async def fetch_total_amount_per_month(year: int, month: int, period: str = "3months") -> float:
    end_date = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc) + timedelta(days=32)
    end_date = end_date.replace(day=1) - timedelta(seconds=1)

    if period == "month":
        start_date = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
    elif period == "year":
        start_date = datetime(year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    else:  # 3months
        start_month = month - 2 if month > 2 else (month - 2) + 12
        start_year = year if month > 2 else year - 1
        start_date = datetime(start_year, start_month, 1, 0, 0, 0, tzinfo=timezone.utc)

    try:
        total_amount = await db.transfers.aggregate([
            {"$match": {"timestamp": {"$gte": start_date, "$lt": end_date}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]).to_list(length=1)

        return round(total_amount[0]["total"], 2) if total_amount else 0.0
    except Exception as e:
        print(f"Error al procesar el total amount por mes: {e}")
        raise

async def fetch_total_amount_per_month_for_company(company_id: str, year: int, month: int) -> float:
    """
    Obtiene el total de las transferencias de un mes específico para una compañía.
    """
    start_date = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
    
    if month < 12:
        end_date = datetime(year, month + 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    else:
        end_date = datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    
    end_date = end_date - timedelta(seconds=1)

    try:
        total_amount = await db.transfers.aggregate([
            {
                "$match": {
                    "timestamp": {"$gte": start_date, "$lt": end_date},
                    "company_id": company_id 
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$amount"}
                }
            }
        ]).to_list(length=1)

        return round(total_amount[0]["total"], 2) if total_amount else 0.0
    except Exception as e:
        print(f"Error al procesar el total amount por mes para la compañía {company_id}: {e}")
        raise


async def fetch_transfer_details(company_id: str, transfer_id: UUID) -> Transfer:
    """
    Fetch details of a specific transfer by ID.
    """
    transfer_id = str(transfer_id)
    
    transfer_doc = await db.transfers.find_one({
        "id": transfer_id,
        "company_id": company_id
    })
    if not transfer_doc:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró la transferencia con el ID {transfer_id}"
        )

    if isinstance(transfer_doc.get("timestamp"), str):
        transfer_doc["timestamp"] = datetime.fromisoformat(transfer_doc["timestamp"])

    return Transfer(**transfer_doc)


async def fetch_public_summary_data() -> Dict[str, Union[int, float]]:
    """
    Obtiene un resumen de todas las transferencias.
    """
    
    try:
        total_transactions = await db.transfers.count_documents({})

        total_anomalies = await db.transfers.count_documents({"is_anomalous": True})

        total_amount = await db.transfers.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]).to_list(length=1)

        return {
            "totalTransactions": total_transactions,
            "totalAnomalies": total_anomalies,
            "totalAmount": round(total_amount[0]["total"], 2) if total_amount else 0.0,
        }
    except Exception as e:
        print(f"Error al procesar el resumen: {e}")
        raise

async def fetch_summary_data_per_month_for_company(company_id: str, year: int, month: int) -> dict:
    """
    Obtiene un resumen de las transferencias para una empresa específica en un mes y año determinados.
    Incluye:
    - Número de transferencias.
    - Número de transferencias anómalas.
    - Monto total de las transferencias.
    """
    start_date = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
    if month < 12:
        end_date = datetime(year, month + 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    else:
        end_date = datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    end_date = end_date - timedelta(seconds=1)

    # Número de transferencias
    transfer_count = await db.transfers.count_documents({
        "company_id": company_id,
        "timestamp": {"$gte": start_date, "$lt": end_date}
    })

    # Número de transferencias anómalas
    anomaly_count = await db.transfers.count_documents({
        "company_id": company_id,
        "is_anomalous": True,
        "timestamp": {"$gte": start_date, "$lt": end_date}
    })

    # Monto total de las transferencias
    try:
        total_amount = await db.transfers.aggregate([
            {
                "$match": {
                    "company_id": company_id,
                    "timestamp": {"$gte": start_date, "$lt": end_date}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$amount"}
                }
            }
        ]).to_list(length=1)

        total_amount = round(total_amount[0]["total"], 2) if total_amount else 0.0
    except Exception as e:
        print(f"Error al procesar el total amount por mes: {e}")
        total_amount = 0.0

    # Resumen
    summary_data = {
        "company_id": company_id,
        "year": year,
        "month": month,
        "totalTransfers": transfer_count,
        "totalAnomalies": anomaly_count,
        "totalAmount": total_amount
    }

    return summary_data

async def fetch_summary(company_id: str) -> Dict[str, Union[int, float]]:
    """
    Obtiene un resumen de las transferencias para una empresa específica.
    """
    try:
        # Total de transacciones
        total_transactions = await db.transfers.count_documents({"company_id": company_id})

        # Total de anomalías detectadas
        total_anomalies = await db.transfers.count_documents(
            {"company_id": company_id, "is_anomalous": True}
        )

        # Monto total transferido
        total_amount = await db.transfers.aggregate([
            {"$match": {"company_id": company_id}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]).to_list(length=1)

        return {
            "totalTransactions": total_transactions,
            "totalAnomalies": total_anomalies,
            "totalAmount": round(total_amount[0]["total"], 2) if total_amount else 0.0,
        }
    except Exception as e:
        print(f"Error al procesar el resumen: {e}")
        raise

async def fetch_new_users_per_month(company_id: str, year: int, month: int) -> int:
    """
    Obtiene los nuevos IBAN (from_account) de un mes específico que no estaban en el mes anterior.
    """
    start_date = datetime(year, month, 1, tzinfo=timezone.utc)
    if month < 12:
        end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)
    else:
        end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    
    prev_start_date = (start_date - timedelta(days=1)).replace(day=1)
    prev_end_date = start_date - timedelta(seconds=1)
    
    current_month_ibans = await db.transfers.distinct("from_account", {
        "company_id": company_id,
        "timestamp": {"$gte": start_date, "$lt": end_date}
    })
    
    previous_month_ibans = await db.transfers.distinct("from_account", {
        "company_id": company_id,
        "timestamp": {"$gte": prev_start_date, "$lt": prev_end_date}
    })

    new_users = len(set(current_month_ibans) - set(previous_month_ibans))
 
    return new_users

async def fetch_transfers_by_range(company_id: str, start_date: datetime, end_date: datetime) -> List[TransferResponse]:
    """
    Devuelve las transferencias en un rango de fechas para una compañía específica.
    """
    transfers = await db.transfers.find({
        "company_id": company_id,
        "timestamp": {"$gte": start_date, "$lte": end_date}
    }).to_list(length=None)
    return transfers

async def fetch_volume_by_day(company_id: str, period: str = Query("3months", enum=["month", "3months", "year"])):
    end_date = datetime.now(timezone.utc)
    if period == "month":
        start_date = end_date - timedelta(days=30)
    elif period == "year":
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=90)

    pipeline = [
        {
            "$match": {
                "company_id": company_id,
                "timestamp": {"$gte": start_date, "$lte": end_date},
            }
        },
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                "count": {"$sum": 1},
            }
        },
        {
            "$sort": {"_id": 1}
        },
        {
            "$project": {
                "date": "$_id",
                "count": 1,
                "_id": 0
            }
        }
    ]

    result = await db.transfers.aggregate(pipeline).to_list(length=100)
    return [{"date": r["date"], "count": r["count"]} for r in result]

async def fetch_anomalous_volume_by_day(company_id: str, period: str = Query("3months", enum=["month", "3months", "year"])):
    end_date = datetime.now(timezone.utc)
    if period == "month":
        start_date = end_date - timedelta(days=30)
    elif period == "year":
        start_date = end_date - timedelta(days=365)
    else: 
        start_date = end_date - timedelta(days=90)

    pipeline = [
        {
            "$match": {
                "company_id": company_id,
                "is_anomalous": True,
                "timestamp": {"$gte": start_date, "$lte": end_date},
            }
        },
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                "count": {"$sum": 1},
            }
        },
        {
            "$sort": {"_id": 1}
        },
        {
            "$project": {
                "date": "$_id",
                "count": 1,
                "_id": 0
            }
        }
    ]

    result = await db.transfers.aggregate(pipeline).to_list(length=100)
    return [{"date": r["date"], "count": r["count"]} for r in result]

async def fetch_status_distribution(company_id: str, period: str = Query("3months", enum=["month", "3months", "year"])):
    end_date = datetime.now(timezone.utc)
    if period == "month":
        start_date = end_date - timedelta(days=30)
    elif period == "year":
        start_date = end_date - timedelta(days=365)
    else: 
        start_date = end_date - timedelta(days=90)

    pipeline = [
        {
            "$match": {
                "company_id": company_id,
                "timestamp": {"$gte": start_date, "$lte": end_date},
            }
        },
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1},
            }
        },
        {
            "$project": {
                "status": "$_id",
                "count": 1,
                "_id": 0
            }
        }
    ]

    result = await db.transfers.aggregate(pipeline).to_list(length=10)
    return [{"status": r["status"], "count": r["count"]} for r in result]



async def get_transfer_stats_by_company(company_id: str) -> Dict[str, Any]:
    """
    Obtiene estadísticas detalladas sobre las transferencias de una empresa específica.
    """
    transfers_collection = db.transfers

    cursor = transfers_collection.find({"company_id": company_id}, {"amount": 1, "from_account": 1})
    data = await cursor.to_list(length=None)

    if not data:
        return {"mean": 0, "std": 0, "q1": 0, "q3": 0, "recurrent_accounts": []}

    df = pd.DataFrame(data)
    amount_mean = df["amount"].mean()
    amount_std = df["amount"].std()
    q1 = df["amount"].quantile(0.05)
    q3 = df["amount"].quantile(0.95)

    # Identificar cuentas recurrentes (aparecen más de una vez para esta compañía)
    recurrent_accounts = df['from_account'].value_counts()[df['from_account'].value_counts() > 1].index.tolist()

    return {
        "mean": amount_mean,
        "std": amount_std,
        "q1": q1,
        "q3": q3,
        "recurrent_accounts": recurrent_accounts
    }
