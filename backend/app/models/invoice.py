from datetime import datetime
from pydantic import BaseModel

from app.models.company import SubscriptionPlan


class Invoice(BaseModel):
    company_id: str
    plan: SubscriptionPlan
    amount: float
    issued_at: datetime
    status: str = "Pagado"