import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def actualizar_categorias():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["nova_track"]
    collection = db["transfers"]

    cambios = {
        "entertainment": "entretenimiento",
        "groceries": "comestibles",
        "utilities": "servicios"
    }

    for ingles, espanol in cambios.items():
        await collection.update_many({"category": ingles}, {"$set": {"category": espanol}})

    print("Categorías actualizadas correctamente.")

asyncio.run(actualizar_categorias())
