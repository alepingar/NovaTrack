from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
collection = db["transfers"]

# Diccionario de valores correctos de ubicación para revertir los cambios
correct_locations = {
    "origin_location": [ "Los Ángeles, EE.UU."],
    "destination_location": [ "Madrid, España"]
}

# Revertir la ubicación_origen y ubicacion_destino a los valores correctos
async def revert_locations():
    # Revertimos los valores de ubicacion_origen

    # Revertimos los valores de ubicacion_destino
    for correct_value in correct_locations["destination_location"]:
        await collection.update_many(
            {"destination_location": "transferencia_bancaria"},  # Reemplazamos "tarjeta_de_crédito"
            {"$set": {"destination_location": correct_value}}
        )

    print("Ubicaciones revertidas correctamente.")

import asyncio
asyncio.run(revert_locations())
