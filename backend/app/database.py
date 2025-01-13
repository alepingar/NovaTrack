from motor.motor_asyncio import AsyncIOMotorClient

# Conectar a MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017/")

# Seleccionar la base de datos
db = client["nova_track"]