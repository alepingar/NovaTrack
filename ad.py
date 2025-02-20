from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
collection = db["transfers"]

async def update_status():
    # Actualizamos el status de las transferencias para que esté en español
    await collection.update_many(
        {"status": "completed"},  # Si el estado es "completed"
        {"$set": {"status": "completada"}}  # Lo cambiamos a "completada"
    )

    await collection.update_many(
        {"status": "pending"},  # Si el estado es "pending"
        {"$set": {"status": "pendiente"}}  # Lo cambiamos a "pendiente"
    )

    await collection.update_many(
        {"status": "failed"},  # Si el estado es "failed"
        {"$set": {"status": "fallida"}}  # Lo cambiamos a "fallida"
    )

    print("Estados actualizados correctamente.")

import asyncio
asyncio.run(update_status())
