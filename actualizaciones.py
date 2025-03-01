from motor.motor_asyncio import AsyncIOMotorClient
import random
from datetime import datetime, timedelta
import asyncio

client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
transfers_collection = db["transfers"]

def generate_random_iban():
    """Genera un IBAN español aleatorio (ESXX XXXX XXXX XX XXXXXXXXXX)."""
    country_code = "ES"
    check_digits = f"{random.randint(10, 99)}"
    bank_code = f"{random.randint(1000, 9999)}"
    branch_code = f"{random.randint(1000, 9999)}"
    control_digits = f"{random.randint(10, 99)}"
    account_number = f"{random.randint(1000000000, 9999999999)}" 
    return f"{country_code}{check_digits}{bank_code}{branch_code}{control_digits}{account_number}"

async def update_timestamps():
    cursor = transfers_collection.find({"timestamp": {"$type": "string"}})

    async for transfer in cursor:
        try:
            new_timestamp = datetime.fromisoformat(transfer["timestamp"])  # Convertir String a datetime
            await transfers_collection.update_one(
                {"_id": transfer["_id"]},
                {"$set": {"timestamp": new_timestamp}}
            )
        except ValueError:
            print(f"Error al convertir timestamp para la transferencia {transfer['_id']}")

    print("Timestamps actualizados correctamente.")

# Ejecutamos la actualización
asyncio.run(update_timestamps())
