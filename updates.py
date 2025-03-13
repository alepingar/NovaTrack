from motor.motor_asyncio import AsyncIOMotorClient
from enum import Enum
import asyncio

# Definir el Enum SubscriptionPlan
class SubscriptionPlan(str, Enum):
    BASICO = "Básico"
    NORMAL = "Normal"
    PRO = "Pro"

# Conectar con MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
companies_collection = db["companies"]

async def update_companies_without_plan():
    # Buscar compañías que no tengan el campo 'subscription_plan'
    query = {"subscription_plan": {"$exists": False}}
    update = {"$set": {"subscription_plan": SubscriptionPlan.BASICO.value}}
    
    # Actualizar todas las compañías que no tienen el campo
    result = await companies_collection.update_many(query, update)
    print(f"✅ Compañías actualizadas: {result.modified_count}")

# Ejecutar la actualización
asyncio.run(update_companies_without_plan())
