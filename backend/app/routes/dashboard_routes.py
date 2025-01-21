from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from app.database import db
from bson import ObjectId
from app.utils.security import get_current_user
router = APIRouter()

@router.get("/")
async def get_dashboard_data(current_user: dict = Depends(get_current_user)):
    company_id = current_user["company_id"]

    # Agrega los cálculos necesarios para los gráficos.
    today = datetime.utcnow()
    one_week_ago = today - timedelta(days=7)

    # Usuarios con más transferencias
    top_users = await db.transfers.aggregate([
        {"$match": {"company_id": ObjectId(company_id)}},
        {"$group": {"_id": "$user_identifier", "transactions": {"$sum": 1}}},
        {"$sort": {"transactions": -1}},
        {"$limit": 5},
    ]).to_list(length=5)

    # Distribución de anomalías
    anomaly_distribution = await db.transfers.aggregate([
        {"$match": {"company_id": ObjectId(company_id)}},
        {"$group": {"_id": "$is_anomalous", "count": {"$sum": 1}}},
    ]).to_list(length=None)

    # Transacciones diarias
    daily_transactions = await db.transfers.aggregate([
        {
            "$match": {
                "company_id": ObjectId(company_id),
                "timestamp": {"$gte": one_week_ago, "$lte": today},
            }
        },
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                "transactions": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]).to_list(length=None)

    return {
        "topUsers": [{"user": user["_id"], "transactions": user["transactions"]} for user in top_users],
        "anomalyDistribution": [
            {"type": "Anómalas" if entry["_id"] else "Normales", "value": entry["count"]}
            for entry in anomaly_distribution
        ],
        "dailyTransactions": [{"date": entry["_id"], "transactions": entry["transactions"]} for entry in daily_transactions],
    }
