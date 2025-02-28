from motor.motor_asyncio import AsyncIOMotorClient
import random

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

async def update_to_account():
    cursor = transfers_collection.find({"from_account": {"$exists": False}})

    async for transfer in cursor:
        iban = generate_random_iban()  # Generar un nuevo IBAN aleatorio
        await transfers_collection.update_one(
            {"_id": transfer["_id"]},
            {"$set": {"from_account": iban}}
        )
    
    print("Transferencias actualizadas con IBAN.")

# Ejecutamos la actualización
import asyncio
asyncio.run(update_to_account())
