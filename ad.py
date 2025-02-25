from motor.motor_asyncio import AsyncIOMotorClient
import random
import re
from bson import ObjectId

client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
transfers_collection = db["transfers"]
companies_collection = db["companies"]

async def generate_valid_iban():
    # Genera un IBAN español aleatorio para las empresas
    country_code = "ES"
    control_digits = random.randint(10, 99)
    bank_code = random.randint(1000, 9999)
    office_code = random.randint(1000, 9999)
    branch_code = random.randint(10, 99)
    account_number = random.randint(1000000000, 9999999999)
    return f"{country_code}{control_digits:02d}{bank_code}{office_code}{branch_code}{account_number}"

async def update_data():
    # 1. Eliminar campo 'to_account' de todas las transferencias
    await transfers_collection.update_many(
        {},
        {"$unset": {"to_account": ""}}  # Elimina el campo 'to_account'
    )
    print("Campo 'to_account' eliminado de todas las transferencias.")

    # 2. Añadir campo 'billing_account_number' con un IBAN válido a todas las empresas

# Ejecutamos la actualización
import asyncio
asyncio.run(update_data())
