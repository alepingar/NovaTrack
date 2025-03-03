import random
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Conectar con MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
comapnies_collection = db["companies"]

# Lista de códigos de bancos reales en España
BANCOS_ESP = [
    "0049",  # Santander
    "0075",  # Banco Popular
    "0081",  # Banco Sabadell
    "2100",  # CaixaBank
    "0182",  # BBVA
    "1465",  # ING
    "0128",  # Bankinter
    "2038",  # Bankia (fusionado con CaixaBank)
]

def generate_iban_es():
    country_code = "ES"
    check_digits = f"{random.randint(10, 99)}"  # Dos dígitos de control
    bank_code = random.choice(BANCOS_ESP)  # Selecciona un banco real
    branch_code = f"{random.randint(1000, 9999)}"  # Código de sucursal (4 dígitos)
    account_number = f"{random.randint(100000000000, 999999999999)}"  # 12 dígitos

    return f"{country_code}{check_digits}{bank_code}{branch_code}{account_number}"

async def update_ibans():
    """Actualiza todos los IBAN en la base de datos con el nuevo formato."""
    cursor = comapnies_collection.find({"billing_account_number": {"$exists": True}})

    async for c in cursor:
        new_iban = generate_iban_es()  # Genera un IBAN correcto
        await comapnies_collection.update_one(
            {"_id": c["_id"]},
            {"$set": {"billing_account_number": new_iban}}
        )

    print("Todos los IBAN han sido actualizados correctamente.")

# Ejecutar la actualización
asyncio.run(update_ibans())
