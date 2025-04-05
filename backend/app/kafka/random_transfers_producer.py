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
# Configuración del productor Kafka
kafka_broker = os.getenv("KAFKA_BROKER", "localhost:9092")  # Valor por defecto para local

# Configuración del productor Kafka
producer_config = {'bootstrap.servers': kafka_broker}
producer = Producer(producer_config)

# Conexión a MongoDB con motor
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]

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
        # Para las anomalías, más probabilidad de "fallida"
        return random.choices(["fallida", "completada", "pendiente"], weights=[70, 20, 10], k=1)[0]
    else:
        # Para las normales, más probabilidad de "completada"
        return random.choices(["completada", "pendiente", "fallida"], weights=[80, 10, 10], k=1)[0]
    
async def get_companies():
    return await db.companies.find({}, {"_id": 1, "name": 1}).to_list(None)

async def get_billing_account_company(company_id: str):
    try:
        company_id_object = ObjectId(company_id)  # Convertir la cadena a ObjectId
        company = await db.companies.find_one({"_id": company_id_object}, {"_id": 1, "billing_account_number": 1})
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
def generate_recurrent_clients(num_clients=10):
    return [generate_iban_es() for _ in range(num_clients)]

async def calculate_avg_amount(company_id):
    try:
        company_id = str(company_id)

        transfers = await db.transfers.find({"company_id": company_id}).to_list(None)

        if not transfers:
            return 10  # Valor mínimo para evitar transferencias con amount = 0

        total_amount = sum(t["amount"] for t in transfers)
        avg_amount = total_amount / len(transfers)

        return avg_amount

    except Exception as e:
        print(f"Error calculando avg_amount: {e}")
        return 10 

async def generate_random_transfer(company_id, recurrent_clients, avg_amount, is_anomalous=False):
    # Definir el rango de los montos, con una distribución alrededor del promedio
    if is_anomalous:
        # 80% de las transferencias anómalas son extremas (mucho más altas o mucho más bajas)
        random_value = random.random()

        if random_value < 0.80:
            # Anomalía muy alta o muy baja
            random_value1 = random.random()
            if random_value1 > 0.5:
                amount = round(random.lognormvariate(np.log(avg_amount * 4), 0.5), 2)  # Anomalía muy alta
            else:
                amount = round(random.uniform(0.01, avg_amount * 0.25), 2)  # Anomalía muy baja

        # 10% de las anomalías son moderadas (±50% del promedio)
        elif random_value < 0.90:
            amount = round(random.uniform(avg_amount * 0.5, avg_amount * 1.5), 2)  # Anomalía moderada

        # 10% de las anomalías son leves (±20% del promedio)
        else:
            amount = round(random.gauss(avg_amount, avg_amount * 0.2 ), 2)  # Anomalía leve

    else:
        # 80% de las transferencias normales son dentro de un rango de +/- 30% del promedio
        random_value = random.random()

        if random_value < 0.80:
            # Transferencias normales (dentro de +/- 30% de la media)
            amount = round(random.gauss(avg_amount, avg_amount * 0.3), 2)

        # 10% de las transferencias normales son dentro de un rango de +/- 50% del promedio
        elif random_value < 0.90:
            amount = round(random.uniform(avg_amount * 0.75, avg_amount * 1.5), 2)  # Transferencia más variable

        # 10% de las transferencias normales son un poco más altas o bajas
        else:
            amount = round(random.uniform(avg_amount * 0.5, avg_amount * 2), 2)  # Rango más amplio

    # No permitir valores negativos
    amount = max(amount, round(random.uniform(0.50, 3.00), 2))
    

    # Generar fecha de transferencia aleatoria (más frecuente en las anomalías)
    days_ago = random.randint(0, 1)  # Solo hoy o ayer
    minutes_ago = random.randint(0, 59)
    seconds_ago = random.randint(0, 59)

    if is_anomalous:
    # Incluir horas dentro y fuera del horario bancario (08:00 - 22:00 y fuera de este rango)
        hours_ago = random.choices(
            population=list(range(0, 8)) + list(range(8, 22)) + list(range(22, 24)),  # Incluye todas las horas
            weights=[0.5] * 8 + [0.1] * 14 + [0.4] * 2,  # Mayor probabilidad fuera del horario normal
            k=1
        )[0]
    else:
        # Horarios bancarios mayoritarios (08:00 - 22:00) con un pequeño porcentaje de fuera de horario
        hours_ago = random.choices(
            population=list(range(8, 22)) + list(range(0, 8)) + list(range(22, 24)),  # Horas normales + raras
            weights=[0.9] * 14 + [0.05] * 8 + [0.05] * 2,  # Mayor probabilidad de horas normales (08:00 - 22:00)
            k=1
        )[0]
        
    # Generar timestamp basado en la configuración
    now = datetime.now(timezone.utc)

    # Retroceder solo los días
    date_base = now - timedelta(days=days_ago)

    # Asignar la hora exacta que generamos, sin cambiar el día incorrectamente
    timestamp_str = datetime(
        year=date_base.year, 
        month=date_base.month, 
        day=date_base.day,  # Mantener el día ya corregido
        hour=hours_ago,  # Asignar la hora correcta
        minute=minutes_ago, 
        second=seconds_ago,
        tzinfo=timezone.utc
    )

    timestamp_str = timestamp_str.isoformat()
    print(timestamp_str)
    # Selección de cuenta de destino (recurrente o nueva)
    use_recurrent = random.choices([True, False], weights=[80, 20])[0]  # 80% recurrente
    from_account = random.choice(recurrent_clients) if use_recurrent else generate_iban_es()

    to_account = await get_billing_account_company(company_id)
    currency = "EUR"

    status = generate_status(is_anomalous)

    return {
        "id": str(uuid.uuid4()),
        "amount": amount,
        "currency": currency,
        "from_account": from_account,
        "to_account": to_account,
        "timestamp": timestamp_str,
        "status": status,
        "company_id": str(company_id)
    }

async def generate_transactions_for_company(company_id, avg_amount, num_transactions):
    transactions = []
    
    # Determinar cuántas transferencias serán anómalas (entre 1 y 10% de las transferencias)
    num_anomalous = max(random.randint(num_transactions // 100, num_transactions // 10), 1) 
    recurrent_clients = generate_recurrent_clients(4)
    
    for i in range(num_transactions):
        is_anomalous = i < num_anomalous
        
        # Generar y agregar transferencia
        transaction = await generate_random_transfer(company_id, recurrent_clients, avg_amount, is_anomalous)
        transactions.append(transaction)
    
    return transactions

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
            num_transactions = random.randint(5, 20)  # Generar entre 5 a 20 transferencias a la vez
            transactions = await generate_transactions_for_company(company["_id"], avg_amount, num_transactions)

            for transfer in transactions:
                producer.produce(
                    'transfers',
                    key=str(transfer["id"]),
                    value=json.dumps(transfer, ensure_ascii=False)
                )
                print(f"Transferencia enviada para {company['name']}: {transfer}")
            producer.flush()
            await asyncio.sleep(random.uniform(40, 120))  # Intervalo entre lotes de transferencias

    except KeyboardInterrupt:
        print("\nGeneración de transferencias interrumpida.")
    finally:
        producer.flush()

if __name__ == "__main__":
    asyncio.run(produce_continuous_transfers())

