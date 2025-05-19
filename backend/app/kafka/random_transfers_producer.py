import time
import random
import uuid
import json
import asyncio
from datetime import datetime, timedelta, timezone
from confluent_kafka import Producer
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import numpy as np
import os
from confluent_kafka import KafkaException
# Configuración del productor Kafka
kafka_broker = os.getenv("KAFKA_BROKER", "localhost:9092")  # Valor por defecto para local

# Configuración del productor Kafka
producer_config = {'bootstrap.servers': kafka_broker}

async def wait_for_kafka_producer(max_retries=20, delay=10): 
    for i in range(max_retries):
        try:
            producer = Producer(producer_config)
            producer.list_topics(timeout=5)
            print("✅ Conectado a Kafka como productor.")
            return producer
        except KafkaException as e:
            print(f"⏳ Kafka no disponible aún (intento {i+1}/{max_retries}): {e}. Esperando {delay}s...")
            await asyncio.sleep(delay) 
    raise Exception("❌ Kafka no está disponible tras varios intentos.")

producer = asyncio.run(wait_for_kafka_producer())

# Conexión a MongoDB con motor
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = AsyncIOMotorClient(MONGO_URI)
db = client["nova_track"]
transfers_collection = db["transfers"]
companies_collection = db["companies"]

# Bancos españoles para IBAN
BANCOS_ESP = ["0049", "0075", "0081", "2100", "0182", "1465", "0128", "2038"]

def generate_iban_es():
    country_code = "ES"
    check_digits = f"{random.randint(10, 99)}"  # Dos dígitos de control
    bank_code = random.choice(BANCOS_ESP)  # Selecciona un banco real
    branch_code = f"{random.randint(1000, 9999)}"  # Código de sucursal (4 dígitos)
    account_number = f"{random.randint(100000000000, 999999999999)}"  # 12 dígitos
    return f"{country_code}{check_digits}{bank_code}{branch_code}{account_number}"

def generate_status(is_anomalous):
    if is_anomalous:
        # Anomalías pueden ser completadas, pero en menor proporción
        return random.choices(["completada", "fallida", "pendiente"], weights=[70, 20, 10], k=1)[0]
    else:
        # Mayoría de transferencias normales son completadas
        return random.choices(["completada", "pendiente", "fallida"], weights=[98, 1, 1], k=1)[0]

async def get_companies():
    return await companies_collection.find({}, {"_id": 1}).to_list(None)

async def get_billing_account_company(company_id: str):
    try:
        company_id_object = ObjectId(company_id)
        company = await companies_collection.find_one({"_id": company_id_object}, {"_id": 1, "billing_account_number": 1})
        if company:
            billing_account = company.get("billing_account_number")
            if billing_account:
                return billing_account
            else:
                print(f"No se encontró el número de cuenta de facturación para la empresa {company_id}")
                return None
        else:
            print(f"No se encontró la empresa con el ID {company_id}")
            return None
    except Exception as e:
        print(f"Error al convertir el ID de empresa: {e}")
        return None

# Generar clientes recurrentes para cada empresa
async def get_recurrent_clients(company_id: str):
    pipeline = [
        {"$match": {"company_id": company_id}},
        {"$group": {"_id": "$from_account", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
        {"$project": {"_id": 1}}
    ]
    recurrent_accounts_data = await transfers_collection.aggregate(pipeline).to_list(length=None)
    return [item['_id'] for item in recurrent_accounts_data]

async def calculate_avg_amount(company_id):
    try:
        transfers = await transfers_collection.find({"company_id": company_id}).to_list(None)
        if not transfers:
            return random.randint(20, 600) # Valor por defecto si no hay transferencias
        total_amount = sum(t["amount"] for t in transfers)
        avg_amount = total_amount / len(transfers)
        return avg_amount
    except Exception as e:
        print(f"Error calculando avg_amount: {e}")
        return random.randint(20, 600)

async def generate_random_transfer(company_id, recurrent_clients, avg_amount, is_anomalous=False):
    # Definir umbrales mínimos y máximos
    MIN_AMOUNT = 3.00  # Evitar valores irreales como céntimos
    MAX_AMOUNT = avg_amount * 10  # Limitar extremos

    if is_anomalous:
        random_value = random.random()

        if random_value < 0.80:
            # 80% de las anomalías son extremas (muy altas o muy bajas)
            if random.random() > 0.5:
                amount = round(random.lognormvariate(np.log(avg_amount * 4), 0.6), 2)  # Mucho más alta
            else:
                amount = round(random.uniform(MIN_AMOUNT, avg_amount * 0.2), 2)  # Mucho más baja

        elif random_value < 0.90:
            # 10% de anomalías moderadas (±50% del promedio)
            amount = round(random.uniform(avg_amount * 0.5, avg_amount * 1.5), 2)

        else:
            # 10% de anomalías leves (±20% del promedio)
            amount = round(random.gauss(avg_amount, avg_amount * 0.2), 2)

    else:
        random_value = random.random()

        if random_value < 0.80:
            # 80% de transferencias normales están dentro de ±25% del promedio
            amount = round(random.gauss(avg_amount, avg_amount * 0.25), 2)

        elif random_value < 0.90:
            # 10% de transferencias normales con más variabilidad
            amount = round(random.uniform(avg_amount * 0.7, avg_amount * 1.7), 2)

        else:
            # 10% de transferencias normales más amplias
            amount = round(random.uniform(avg_amount * 0.4, avg_amount * 2.5), 2)

    # Asegurar que el monto esté dentro de los límites realistas
    amount = max(amount, MIN_AMOUNT)
    amount = min(amount, MAX_AMOUNT)

    today = datetime.now(timezone.utc)
    first_day_of_year = datetime(today.year, 1, 1, tzinfo=timezone.utc)
    days_since_first_day = (today - first_day_of_year).days

    # Definir los pesos según el día de la semana para cada caso
    if is_anomalous:
        # Para anomalías, se da mayor peso a inicios de semana por el proceso de concentración de operaciones
        day_weights = {0: 25, 1: 20, 2: 15, 3: 15, 4: 15, 5: 5, 6: 5}
    else:
        # Transferencias normales se concentran en días laborables
        day_weights = {0: 18, 1: 20, 2: 17, 3: 17, 4: 15, 5: 7, 6: 6}

    # Generar la lista de posibles días (en "días atrás" desde hoy)
    population = range(3, days_since_first_day + 1) # Incluir el día actual
    # Para cada día posible, asignamos el peso correspondiente en función del día de la semana
    weights_list = [
        day_weights[(today - timedelta(days=x)).weekday()] for x in population
    ]

    # Elegimos un "days_ago" en función de las ponderaciones
    days_ago = random.choices(population=list(population), weights=weights_list, k=1)[0]

    # Generar la hora
    minutes_ago = random.randint(0, 59)
    seconds_ago = random.randint(0, 59)

    if is_anomalous:
        hours_ago = random.choices(
            population=list(range(0, 8)) + list(range(8, 22)) + list(range(22, 24)),
            weights=[0.3] * 8 + [0.4] * 14 + [0.3] * 2,
            k=1
        )[0]
    else:
        hours_ago = random.choices(
            population=list(range(8, 22)) + list(range(0, 8)) + list(range(22, 24)),
            weights=[0.9] * 14 + [0.05] * 8 + [0.05] * 2,
            k=1
        )[0]

    # Fecha base ajustada
    now = datetime.now(timezone.utc)
    date_base = now - timedelta(days=days_ago)

    # Timestamp final con la hora exacta
    timestamp = datetime(
        year=date_base.year,
        month=date_base.month,
        day=date_base.day,
        hour=hours_ago,
        minute=minutes_ago,
        second=seconds_ago,
        tzinfo=timezone.utc
    )

    if(is_anomalous):
        use_recurrent = random.choices([True, False], weights=[30, 70])[0]
        if use_recurrent and recurrent_clients:
            from_account = random.choice(recurrent_clients)  # Cliente conocido
        else:
            from_account = generate_iban_es()  # Nuevo remitente
    else:
    # Para las transferencias normales, 80% provienen de clientes recurrentes
        use_recurrent = random.choices([True, False], weights=[80, 20])[0]  # 80% recurrente, 20% no recurrente

        if use_recurrent and recurrent_clients:
            from_account = random.choice(recurrent_clients)  # Cliente recurrente
        else:
            from_account = generate_iban_es()  # Nuevo cliente

    to_account = await get_billing_account_company(company_id)  # 80% de probabilidad de ser un IBAN español
    # Obtener la moneda del país de destino
    currency =  "EUR" # Si no está en el diccionario, por defecto EUR

    # Determinar el estado de la transferencia
    status = generate_status(is_anomalous)

    return {
        "id": str(uuid.uuid4()),  # ID único con UUID
        "amount": amount,  # Monto en EUR
        "currency": currency,  # Moneda según el IBAN de destino
        "from_account": from_account,
        "to_account": to_account,
        "timestamp": timestamp.isoformat(),
        "status": status,
        "company_id": str(company_id),
    }

async def produce_continuous_transfers():
    companies = []
    last_companies_update = datetime.now()
    companies_update_interval = timedelta(minutes=2)  # Intervalo de actualización

    try:
        companies = await get_companies()
        if not companies:
            print("No hay empresas en la base de datos.")
            return 
        print(f"Lista de empresas inicializada: {[str(company['_id']) for company in companies]}")
        while True:
            # Recargar la lista de empresas periódicamente
            if datetime.now() - last_companies_update > companies_update_interval:
                companies = await get_companies()
                if not companies:
                    print("No hay empresas en la base de datos.")
                    await asyncio.sleep(60)  # Esperar antes de volver a intentar
                    continue
                print(f"Lista de empresas actualizada: {[str(company['_id']) for company in companies]}")
                last_companies_update = datetime.now()

            if not companies:
                print("No hay empresas en la base de datos. Esperando la inicialización...")
                await asyncio.sleep(60)  # Esperar antes de volver a intentar
                continue

            company = random.choice(companies)
            company_id = str(company["_id"])
            avg_amount = await calculate_avg_amount(company_id)
            recurrent_clients = await get_recurrent_clients(company_id)
            num_transactions = random.randint(5, 20)

            for _ in range(num_transactions):
                is_anomalous = random.random() < 0.075
                transfer = await generate_random_transfer(company_id, recurrent_clients, avg_amount, is_anomalous)
                producer.produce('transfers', key=str(transfer["id"]), value=json.dumps(transfer, ensure_ascii=False))
                print(f"Transferencia enviada para la empresa {company_id}: {transfer}")
            producer.flush(timeout=3)
            await asyncio.sleep(random.uniform(40, 120))  # Intervalo más corto para flujo continuo

    except KeyboardInterrupt:
        print("\nGeneración de transferencias interrumpida.")
    finally:
        producer.flush(timeout=3)

if __name__ == "__main__":
    asyncio.run(produce_continuous_transfers())