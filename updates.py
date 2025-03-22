from motor.motor_asyncio import AsyncIOMotorClient
from random import choice
import asyncio
from datetime import datetime, timezone

# Conectar con MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
companies_collection = db["companies"]

async def update_gdpr_logs():
    companies = companies_collection.find()
    async for company in companies:
        gdpr_action = choice(["delete", "access"])
        gdpr_entry = {"action": gdpr_action}
        
        # Actualizar la compañía agregando el log GDPR
        await companies_collection.update_one(
            {"_id": company["_id"]},
            {"$set": {"gdpr_request_log": [gdpr_entry]}}
        )
        print(f"✅ Empresa {company['name']} actualizada con GDPR log: {gdpr_action}")

# Ejecutar la actualización
asyncio.run(update_gdpr_logs())
