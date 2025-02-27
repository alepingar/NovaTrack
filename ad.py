from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
transfers_collection = db["transfers"]

async def update_data():
    # 1. Eliminar los campos innecesarios
    await transfers_collection.update_many(
        {},
        {
            "$unset": {
                "description": "",  # Elimina el campo 'description'
                "origin_location": "",  # Elimina el campo 'origin_location'
                "payment_method": "",  # Elimina el campo 'payment_method'
                "user_identifier": "",  # Elimina el campo 'user_identifier'
                "is_recurring": "",  # Elimina el campo 'is_recurring'
                "device_fingerprint": "",  # Elimina el campo 'device_fingerprint'
                "client_ip": "",  # Elimina el campo 'client_ip'
                "linked_order_id": ""  # Elimina el campo 'linked_order_id'
            }
        }
    )
    print("Campos innecesarios eliminados de todas las transferencias.")

# Ejecutamos la actualización
import asyncio
asyncio.run(update_data())
