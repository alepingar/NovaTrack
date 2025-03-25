from typing import List
from fastapi import APIRouter, Depends

from app.models.invoice import Invoice
from app.services.invoice_service import get_invoices_per_company
from app.utils.security import get_current_user


router = APIRouter()



@router.get("/", response_model=List[Invoice])
async def get_invoices(current_user: dict = Depends(get_current_user)):

    return await get_invoices_per_company(current_user["company_id"])
