from app.database import db
from app.schemas import Transfer, TransferResponse
from datetime import datetime, timedelta
from typing import List
from fastapi import HTTPException
from typing import Dict, Union


async def fetch_transfers(company_id: str) -> List[TransferResponse]:
    """
    Fetch all transfers for a given company.
    """
    transfers = await db.transfers.find({"company_id": company_id}).to_list(length=100)
    return transfers

async def fetch_transfer_details(company_id: str, transfer_id: int) -> Transfer:
    """
    Fetch details of a specific transfer by ID.
    """
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


async def fetch_volume_by_day(company_id: str):
    result = await db.transfers.aggregate([
        {"$match": {"company_id": company_id}},
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]).to_list(length=100)
    return [{"date": r["_id"], "count": r["count"]} for r in result]


async def fetch_amount_by_category(company_id: str):
    result = await db.transfers.aggregate([
        {"$match": {"company_id": company_id}},
        {"$group": {"_id": "$category", "totalAmount": {"$sum": "$amount"}}},
        {"$sort": {"totalAmount": -1}}
    ]).to_list(length=10)
    return [{"category": r["_id"], "amount": r["totalAmount"]} for r in result if r["_id"]]


async def fetch_status_distribution(company_id: str):
    result = await db.transfers.aggregate([
        {"$match": {"company_id": company_id}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]).to_list(length=10)
    return [{"status": r["_id"], "count": r["count"]} for r in result]


async def fetch_top_origin_locations(company_id: str):
    result = await db.transfers.aggregate([
        {"$match": {"company_id": company_id}},
        {"$group": {"_id": "$origin_location", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]).to_list(length=5)
    return [{"location": r["_id"], "count": r["count"]} for r in result if r["_id"]]
