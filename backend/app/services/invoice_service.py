from typing import List
from app.database import db
from app.models.invoice import Invoice


async def get_invoices_per_company(company_id: str) -> List[Invoice]:

     invoices = await db.invoices.find({"company_id": company_id}, {"_id": 0}).to_list(7)  
     print("Facturas encontradas:", invoices)
     return invoices