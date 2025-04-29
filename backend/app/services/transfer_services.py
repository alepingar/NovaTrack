from logging import log
import logging
import pandas as pd
from app.database import db
from app.models.transfer import Transfer, TransferResponse
from datetime import datetime, timezone, timedelta
from typing import Any, List, Optional
from fastapi import HTTPException
from typing import Dict, Union
from uuid import UUID
from pymongo import ReturnDocument

log = logging.getLogger(__name__)

async def fetch_transfers(company_id: str) -> List[TransferResponse]:
    """
    Fetch all transfers for a given company.
    """
    transfers = await db.transfers.find({"company_id": company_id}).to_list()
    return transfers

async def mark_transfer_as_normal(transfer_id: UUID, company_id: str) -> TransferResponse: 
    """
    Marks a specific transfer as not anomalous (is_anomalous = False).
    Simplified version: First finds, then updates. USES PRINT FOR DEBUGGING.
    """
    transfer_id_str = str(transfer_id)
    find_filter = {"id": transfer_id_str, "company_id": company_id}
    transfer_doc = await db.transfers.find_one(find_filter)

    if not transfer_doc:
        print(f"--- PRINT: Mark Normal - Service --- CRITICAL: find_one FAILED for filter {find_filter}, but GET succeeded previously?")
        raise HTTPException(
            status_code=404,
            detail=f"Transfer with ID {transfer_id_str} not found for this company (inconsistency detected)."
        )

    update_filter = {"id": transfer_id_str, "company_id": company_id} 
    update_operation = {"$set": {"is_anomalous": False}}

    try:
        update_result = await db.transfers.update_one(update_filter, update_operation)
        
        if update_result.matched_count == 0:
             raise HTTPException(status_code=404, detail="Transfer found but could not be matched for update.")

        if update_result.modified_count == 1 or (update_result.matched_count == 1 and update_result.modified_count == 0):
             if update_result.modified_count == 1:
                  # Reemplazo de log.info
                  print(f"--- PRINT: Mark Normal - Service --- update_one SUCCEEDED. Transfer id='{transfer_id_str}' marked as normal.")
             else:
                  # Reemplazo de log.warning
                  print(f"--- PRINT: Mark Normal - Service --- update_one matched but modified 0 documents for filter {update_filter}. Transfer possibly already marked normal.")

             transfer_doc['is_anomalous'] = False
             if '_id' in transfer_doc and 'id' not in transfer_doc:
                  transfer_doc['id'] = str(transfer_doc.pop('_id'))
             elif 'id' in transfer_doc and isinstance(transfer_doc['id'], UUID):
                  transfer_doc['id'] = str(transfer_doc['id'])

             if '_id' in transfer_doc:
                 transfer_doc['_id'] = str(transfer_doc['_id'])

             try:
                 return TransferResponse(**transfer_doc)
             except Exception as pydantic_error:
                 raise HTTPException(status_code=500, detail="Failed to format response after update.")

        else:
             raise HTTPException(status_code=500, detail="Unexpected error during transfer update.")

    except Exception as e:
        if isinstance(e, HTTPException):
             raise e 
        else:
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while updating the transfer status."
            )

    except Exception as e:
        log.error(f"[Mark Normal - Service] Database error during update_one for id='{transfer_id_str}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating the transfer status."
        )
    
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

  
    recurrent_accounts = df['from_account'].value_counts()[df['from_account'].value_counts() > 1].index.tolist()

    return {
        "mean": amount_mean,
        "std": amount_std,
        "q1": q1,
        "q3": q3,
        "recurrent_accounts": recurrent_accounts
    }

async def fetch_dashboard_data_internal(
    company_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    bank_prefix: Optional[str] = None, 
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
) -> Dict[str, Any]:
    """
    Función interna para calcular todos los datos del dashboard aplicando filtros.
    """

    query = {"company_id": company_id} # Query base

    date_query = {}
    if start_date and end_date:
        start_date_aware = start_date.replace(tzinfo=timezone.utc) if start_date.tzinfo is None else start_date
        end_date_aware = end_date.replace(tzinfo=timezone.utc) if end_date.tzinfo is None else end_date
        end_date_aware = end_date_aware.replace(hour=23, minute=59, second=59, microsecond=999999)
        date_query = {"$gte": start_date_aware, "$lte": end_date_aware}
        query["timestamp"] = date_query
    elif start_date:
        start_date_aware = start_date.replace(tzinfo=timezone.utc) if start_date.tzinfo is None else start_date
        date_query = {"$gte": start_date_aware}
        query["timestamp"] = date_query
    elif end_date:
        end_date_aware = end_date.replace(tzinfo=timezone.utc) if end_date.tzinfo is None else end_date
        end_date_aware = end_date_aware.replace(hour=23, minute=59, second=59, microsecond=999999)
        date_query = {"$lte": end_date_aware}
        query["timestamp"] = date_query

    if bank_prefix and bank_prefix.strip():
        cleaned_prefix = bank_prefix.strip()

        if len(cleaned_prefix) == 4 and cleaned_prefix.isdigit():
            bank_regex = f"^.{{4}}{cleaned_prefix}"
            query["from_account"] = {"$regex": bank_regex}
        else:

            log.warning(f"[DB] Invalid bank_prefix format received: '{bank_prefix}'. Bank filter NOT applied.")

    else:
         log.info("[DB] No valid bank_prefix provided, skipping bank filter.")

    amount_query = {}
    if min_amount is not None and max_amount is not None:
        amount_query = {"$gte": min_amount, "$lte": max_amount}
    elif min_amount is not None:
        amount_query = {"$gte": min_amount}
    elif max_amount is not None:
        amount_query = {"$lte": max_amount}
    if amount_query:
         query["amount"] = amount_query


    try:
        # 1. Resumen General
        pipeline_summary = [{"$match": query}, {"$group": { "_id": None, "totalTransactions": {"$sum": 1}, "totalAnomalies": {"$sum": {"$cond": ["$is_anomalous", 1, 0]}}, "totalAmount": {"$sum": "$amount"} }}]
        summary_data = await db.transfers.aggregate(pipeline_summary).to_list(length=1)
        summary = { "totalTransactions": summary_data[0]["totalTransactions"] if summary_data else 0, "totalAnomalies": summary_data[0]["totalAnomalies"] if summary_data else 0, "totalAmount": round(summary_data[0]["totalAmount"], 2) if summary_data else 0.0 }

        # 2. Nuevos Remitentes (Únicos en periodo)
        distinct_senders = await db.transfers.distinct("from_account", query)
        summary["newSenders"] = len(distinct_senders)

        # 3. Volumen por Día (Total)
        pipeline_volume = [ {"$match": query}, {"$match": {"timestamp": {"$type": "date"}}}, {"$group": { "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp", "timezone": "UTC"}}, "count": {"$sum": 1} }}, {"$sort": {"_id": 1}}, {"$project": {"date": "$_id", "count": 1, "_id": 0}} ]
        volume_by_day = await db.transfers.aggregate(pipeline_volume).to_list(length=None)

        # 4. Volumen por Día (Anomalías)
        query_anomalous = {**query, "is_anomalous": True}
        pipeline_anomalous_volume = [ {"$match": query_anomalous}, {"$match": {"timestamp": {"$type": "date"}}}, {"$group": { "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp", "timezone": "UTC"}}, "count": {"$sum": 1} }}, {"$sort": {"_id": 1}}, {"$project": {"date": "$_id", "count": 1, "_id": 0}} ]
        anomalous_volume_by_day = await db.transfers.aggregate(pipeline_anomalous_volume).to_list(length=None)
     
        # 5. Distribución de Estados

        pipeline_status = [ {"$match": query}, {"$group": {"_id": "$status", "count": {"$sum": 1}}}, {"$project": {"status": "$_id", "count": 1, "_id": 0}} ]
        status_distribution = await db.transfers.aggregate(pipeline_status).to_list(length=None)

        # 6. Monto Agrupado por Mes (filtrado)

        pipeline_amount_monthly = [ {"$match": query}, {"$match": {"timestamp": {"$type": "date"}}}, {"$group": { "_id": { "year": {"$year": {"date": "$timestamp", "timezone": "UTC"}}, "month": {"$month": {"date": "$timestamp", "timezone": "UTC"}} }, "monthlyAmount": {"$sum": "$amount"} }}, {"$sort": {"_id.year": 1, "_id.month": 1}}, {"$project": { "year": "$_id.year", "month": "$_id.month", "amount": {"$round": ["$monthlyAmount", 2]}, "_id": 0 }} ]
        amount_by_month_filtered = await db.transfers.aggregate(pipeline_amount_monthly).to_list(length=None)

        summaryP = {"totalTransfers": 0, "totalAnomalies": 0, "totalAmount": 0.0}
        summaryPA = {"totalTransfers": 0, "totalAnomalies": 0, "totalAmount": 0.0}

    except Exception as e:
        log.error(f"[DB] Error during MongoDB aggregation: {e}", exc_info=True) 

        raise

    return {
        "summary": summary,
        "summaryPreviousMonth": summaryP,
        "summaryMonthBeforePrevious": summaryPA,
        "volumeByDay": volume_by_day,
        "anomalousVolumeByDay": anomalous_volume_by_day,
        "statusDistribution": status_distribution,
        "amountByMonth": amount_by_month_filtered
    }



async def fetch_transfers_by_filters(
    company_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    bank_prefix: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
) -> List[Dict[str, Any]]: 
    """
    Devuelve una LISTA de transferencias que coinciden con los filtros
    proporcionados para una compañía específica.
    """
    query = {"company_id": company_id}

    if start_date and end_date:
        start_date_aware = start_date.replace(tzinfo=timezone.utc) if start_date.tzinfo is None else start_date
        end_date_aware = end_date.replace(tzinfo=timezone.utc) if end_date.tzinfo is None else end_date
        end_date_aware = end_date_aware.replace(hour=23, minute=59, second=59, microsecond=999999)
        query["timestamp"] = {"$gte": start_date_aware, "$lte": end_date_aware}
    elif start_date:
        start_date_aware = start_date.replace(tzinfo=timezone.utc) if start_date.tzinfo is None else start_date
        query["timestamp"] = {"$gte": start_date_aware}
    elif end_date:
        end_date_aware = end_date.replace(tzinfo=timezone.utc) if end_date.tzinfo is None else end_date
        end_date_aware = end_date_aware.replace(hour=23, minute=59, second=59, microsecond=999999)
        query["timestamp"] = {"$lte": end_date_aware}


    if bank_prefix and bank_prefix.strip():
        cleaned_prefix = bank_prefix.strip()
        if len(cleaned_prefix) == 4 and cleaned_prefix.isdigit():
            bank_regex = f"^.{{4}}{cleaned_prefix}"
            query["from_account"] = {"$regex": bank_regex}
        else:
             log.warning(f"[DB Table] Invalid bank_prefix format received: '{bank_prefix}'. Filter not applied.")

   
    amount_query = {}
    if min_amount is not None and max_amount is not None:
        amount_query = {"$gte": min_amount, "$lte": max_amount}
    elif min_amount is not None:
        amount_query = {"$gte": min_amount}
    elif max_amount is not None:
        amount_query = {"$lte": max_amount}
    if amount_query:
         query["amount"] = amount_query

    try:
        transfers_cursor = db.transfers.find(query).sort("timestamp", -1)
        transfers = await transfers_cursor.to_list(length=None) 

        return transfers 
    except Exception as e:
        log.error(f"[DB Table] Error fetching filtered transfer list: {e}", exc_info=True)

        raise HTTPException(status_code=500, detail="Error retrieving transfer list")

async def fetch_transfers1(company_id: str) -> List[Dict[str, Any]]: 
    """
    Obtiene TODAS las transferencias para una compañía dada (sin filtros).
    """
    try:
        transfers_cursor = db.transfers.find({"company_id": company_id}).sort("timestamp", -1)
        transfers = await transfers_cursor.to_list(length=None)
        return transfers
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving all transfers")