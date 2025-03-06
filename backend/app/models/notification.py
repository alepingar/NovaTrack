from datetime import datetime
from pydantic import BaseModel

class Notification(BaseModel):
    message: str
    timestamp: datetime
    type: str
    company_id: str