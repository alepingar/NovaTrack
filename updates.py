from motor.motor_asyncio import AsyncIOMotorClient
from enum import Enum

# Conectar con MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
companies_collection = db["companies"]

# Definir los planes de suscripción en mayúsculas
class SubscriptionPlan(str, Enum):
    BASICO = "BASICO"
    NORMAL = "NORMAL"
    PRO = "PRO"

async def update_subscription_plans():
    companies = companies_collection.find()
    async for company in companies:
        # Obtener el plan de suscripción actual en minúsculas
        current_plan = company.get("subscription_plan", "").upper()
        
        # Verificar si el plan existe y es uno válido
        if current_plan in [plan.value for plan in SubscriptionPlan]:
            updated_plan = current_plan
        else:
            # Si el plan no es válido, asignar el valor predeterminado
            updated_plan = SubscriptionPlan.BASICO.value

        # Actualizar el plan de suscripción en la base de datos
        await companies_collection.update_one(
            {"_id": company["_id"]},
            {"$set": {"subscription_plan": updated_plan}}
        )
        print(f"✅ Empresa {company['name']} actualizada con plan de suscripción: {updated_plan}")

# Ejecutar la actualización
import asyncio
asyncio.run(update_subscription_plans())
