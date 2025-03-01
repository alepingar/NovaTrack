import random
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Conectar con MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
transfers_collection = db["transfers"]

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
    """Genera un IBAN español realista con códigos de bancos válidos."""
    country_code = "ES"
    check_digits = f"{random.randint(10, 99)}"  # Dos dígitos de control
    bank_code = random.choice(BANCOS_ESP)  # Banco real
    branch_code = f"{random.randint(1000, 9999)}"  # Código de sucursal
    control_digits = f"{random.randint(10, 99)}"  # Dígitos de control
    account_number = f"{random.randint(1000000000, 9999999999)}"  # 10 dígitos

    return f"{country_code}{check_digits}{bank_code}{branch_code}{control_digits}{account_number}"

async def update_ibans():
    """Actualiza todos los IBAN en la base de datos con el nuevo formato."""
    cursor = transfers_collection.find({"from_account": {"$exists": True}})

    async for transfer in cursor:
        new_iban = generate_iban_es()  # Genera un IBAN correcto
        await transfers_collection.update_one(
            {"_id": transfer["_id"]},
            {"$set": {"from_account": new_iban}}
        )

    print("Todos los IBAN han sido actualizados correctamente.")

# Ejecutar la actualización
asyncio.run(update_ibans())
