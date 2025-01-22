from app.database import db
from app.schemas import Transfer, TransferResponse
from datetime import datetime
from typing import List
from fastapi import HTTPException
from pydantic import ValidationError

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

async def fetch_summary(company_id: str):
    """
    Generate a summary of transactions for a given company.
    """
    try:
        total_transactions = await db.transfers.count_documents({"company_id": company_id})
        total_anomalies = await db.transfers.count_documents(
            {"company_id": company_id, "is_anomalous": True}
        )
        total_amount = await db.transfers.aggregate([
            {"$match": {"company_id": company_id}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]).to_list(length=1)

        return {
            "totalTransactions": total_transactions,
            "totalAnomalies": total_anomalies,
            "totalAmount": total_amount[0]["total"] if total_amount else 0.0,
        }
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Error de validación: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

async def fetch_anomalies(company_id: str) -> List[TransferResponse]:
    """
    Fetch the most recent anomalous transactions for a given company.
    """
    anomalies = await db.transfers.find(
        {"company_id": company_id, "is_anomalous": True}
    ).sort("timestamp", -1).to_list(length=10)

    sanitized_anomalies = [
        {
            "id": anomaly.get("id", 0),
            "amount": anomaly.get("amount", 0.0),
            "from_account": anomaly.get("from_account", "Unknown"),
            "to_account": anomaly.get("to_account", "Unknown"),
            "timestamp": datetime.fromisoformat(anomaly["timestamp"]) if isinstance(anomaly["timestamp"], str) else anomaly["timestamp"],
            "status": anomaly.get("status", "unknown"),
            "is_anomalous": anomaly.get("is_anomalous", False),
            "description": anomaly.get("description", None),
        }
        for anomaly in anomalies
    ]

    try:
        validated_anomalies = [TransferResponse(**anomaly) for anomaly in sanitized_anomalies]
        return validated_anomalies
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Error de validación: {str(e)}")
