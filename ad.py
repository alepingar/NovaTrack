from motor.motor_asyncio import AsyncIOMotorClient
import random
import re
from bson import ObjectId

client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
transfers_collection = db["transfers"]

async def update_data():
    # 1. Eliminar los campos 'destination_location', 'category' y 'transaction_fee' de todas las transferencias
    await transfers_collection.update_many(
        {},
        {
            "$unset": {
                "destination_location": "",  # Elimina el campo 'destination_location'
                "category": "",  # Elimina el campo 'category'
                "transaction_fee": ""  # Elimina el campo 'transaction_fee'
            }
        }
    )
    print("Campos 'destination_location', 'category' y 'transaction_fee' eliminados de todas las transferencias.")

    # 2. Añadir campo 'billing_account_number' con un IBAN válido a todas las empresas

# Ejecutamos la actualización
import asyncio
asyncio.run(update_data())
