from fastapi import APIRouter, Depends, HTTPException
from app.database import db
from app.schemas import TransferResponse
from app.utils.security import get_current_user
from typing import List

router = APIRouter()

@router.get("/transfers", response_model=List[TransferResponse])
async def get_transfers(current_user: dict = Depends(get_current_user)):
    """
    Obtiene las transferencias asociadas a la empresa actual.
    """
    company_id = current_user["company_id"]
    transfers = await db.transfers.find({"company_id": company_id}).to_list(length=100)
    return transfers
