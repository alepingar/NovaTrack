from motor.motor_asyncio import AsyncIOMotorClient
import os
# Conectar a MongoDB
client = AsyncIOMotorClient(os.getenv("MONGO_URI"))

# Seleccionar la base de datos
db = client["nova_track"]