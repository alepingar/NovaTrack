import time
import random
import uuid
import json
import asyncio
from datetime import datetime, timezone  # Corrección aquí
from confluent_kafka import Producer
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
# Configuración del productor Kafka
producer_config = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(producer_config)

# Conexión a MongoDB con motor
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]

# Diccionario de monedas por país
currency_by_country = {"ES": "EUR", "FR": "EUR", "DE": "EUR", "GB": "GBP", "US": "USD"}

# Bancos españoles para IBAN
BANCOS_ESP = ["0049", "0075", "0081", "2100", "0182", "1465", "0128", "2038"]

def generate_iban_es():
    country_code = "ES"
    check_digits = f"{random.randint(10, 99)}"
    bank_code = random.choice(BANCOS_ESP)
    branch_code = f"{random.randint(1000, 9999)}"
    account_number = f"{random.randint(1000000000, 9999999999)}"
    return f"{country_code}{check_digits}{bank_code}{branch_code}{account_number}"

def generate_status():
    return random.choices(["completada", "pendiente", "fallida"], weights=[80, 10, 10], k=1)[0]

def generate_random_transfer(company_id, avg_amount):
    amount = round(random.uniform(avg_amount * 0.5, avg_amount * 1.5), 2)
    timestamp = datetime.now(timezone.utc)
    from_account = generate_iban_es()
    to_account = "ES2071549200121562384309"
    to_country_code = from_account[:2]
    currency = currency_by_country.get(to_country_code, "EUR")
    status = generate_status()
    
    return {
        "id": str(uuid.uuid4()),
        "amount": amount,
        "currency": currency,
        "from_account": from_account,
        "to_account": to_account,
        "timestamp": timestamp.isoformat(),
        "status": status,
        "company_id": str(company_id)
    }

async def get_companies():
    return await db.companies.find({}, {"_id": 1, "name": 1}).to_list(None)

async def calculate_avg_amount(company_id):
    try:
        # Convertimos a ObjectId si no lo es
        if not isinstance(company_id, ObjectId):
            company_id = ObjectId(company_id)

        transfers = await db.transfers.find({"company_id": company_id}).to_list(None)

        if not transfers:
            return 10  # Valor mínimo para evitar transferencias con amount = 0

        total_amount = sum(t["amount"] for t in transfers)
        avg_amount = total_amount / len(transfers)

        return avg_amount

    except Exception as e:
        print(f"Error calculando avg_amount: {e}")
        return 10 

async def produce_continuous_transfers():
    companies = await get_companies()
    if not companies:
        print("No hay empresas en la base de datos.")
        return
    print(f"Empresas encontradas: {[company['name'] for company in companies]}")
    try:
        while True:
            company = random.choice(companies)
            avg_amount = await calculate_avg_amount(company["_id"])
            transfer = generate_random_transfer(company["_id"], avg_amount)
            producer.produce(
                'transfers',
                key=str(transfer["id"]),
                value=json.dumps(transfer, ensure_ascii=False)
            )
            producer.flush()
            print(f"Transferencia enviada para {company['name']}: {transfer}")
            await asyncio.sleep(random.uniform(40, 120))
    except KeyboardInterrupt:
        print("\nGeneración de transferencias interrumpida.")
    finally:
        producer.flush()

if __name__ == "__main__":
    asyncio.run(produce_continuous_transfers())
