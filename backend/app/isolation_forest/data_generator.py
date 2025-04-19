from motor.motor_asyncio import AsyncIOMotorClient
import random
import uuid
from datetime import datetime, timedelta, timezone
from bson import ObjectId
import numpy as np
import os


# Conexión a la base de datos MongoDB

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = AsyncIOMotorClient(MONGO_URI)
db = client["nova_track"]
transfers_collection = db["transfers"]

# Genera IBAN español válido
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

# Generar clientes recurrentes para cada empresa
def generate_recurrent_clients(num_clients):
    return [generate_iban_es() for _ in range(num_clients)]

# Función para seleccionar el estado de la transferencia
def generate_status(is_anomalous):
    if is_anomalous:
        # Anomalías pueden ser completadas, pero en menor proporción
        return random.choices(["completada", "fallida", "pendiente"], weights=[70, 20, 10], k=1)[0]
    else:
        # Mayoría de transferencias normales son completadas
        return random.choices(["completada", "pendiente", "fallida"], weights=[98, 1, 1], k=1)[0]

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

# Genera una transferencia aleatoria
async def generate_random_transfer(company_id,recurrent_clients, avg_amount, is_anomalous=False):
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
    population = range(3, days_since_first_day)
    # Para cada día posible, asignamos el peso correspondiente en función del día de la semana
    weights_list = [
        day_weights[(today - timedelta(days=x)).weekday()] for x in population
    ]
    
    # Elegimos un "days_ago" en función de las ponderaciones
    days_ago = random.choices(population=population, weights=weights_list, k=1)[0]

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
        if use_recurrent:
            from_account = random.choice(recurrent_clients)  # Cliente conocido
        else:
            from_account = generate_iban_es()  # Nuevo remitente
    else:
    # Para las transferencias normales, 80% provienen de clientes recurrentes
        use_recurrent = random.choices([True, False], weights=[80, 20])[0]  # 80% recurrente, 20% no recurrente
        
        if use_recurrent:
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
        "timestamp": timestamp,
        "status": status,
        "company_id": str(company_id),
        "is_anomalous": is_anomalous,
    }

async def generate_transactions_for_company(company_id,num_transactions=1000):
    transactions = []
    # Determinar un rango realista para el número de clientes recurrentes
    company_size_factor = random.choice(['small', 'medium', 'large'])
    if company_size_factor == 'small':
        recurrent_clients_count = random.randint(20, 50)  # Empresas pequeñas tendrán menos clientes
        avg_amount = random.randint(20, 100)  # Promedio para pequeñas empresas
        num_transactions = random.randint(200, 500)
    elif company_size_factor == 'medium':
        recurrent_clients_count = random.randint(50, 150)  # Empresas medianas
        avg_amount = random.randint(100, 300)  # Promedio para medianas empresas
        num_transactions = random.randint(500, 1500)
    else:  # large
        recurrent_clients_count = random.randint(100, 300)  # Empresas grandes (pero aún PYMEs)
        avg_amount = random.randint(300, 600)  # Promedio para grandes empresas
        num_transactions = random.randint(1500, 3000)
    
    recurrent_clients = generate_recurrent_clients(recurrent_clients_count)
    
    mean_anomalies = 0.075 * num_transactions
    std_dev = mean_anomalies * 0.5
    num_anomalous = int(np.random.normal(mean_anomalies, std_dev))
    num_anomalous = max(0, min(num_anomalous, num_transactions))
    anomaly_rate = num_anomalous / num_transactions
    
    # Generar las transferencias
    for i in range(num_transactions):
        is_anomalous = random.random() < anomaly_rate   
        # Generar el monto realista usando una distribución normal ajustada a PYMEs
        amount = avg_amount  # 15% de desviación estándar para no generar montos extremos
        amount = max(5, min(amount, 2000))  # Asegurar que el monto esté en un rango realista para PYMEs (10 - 1000 EUR)
        
        # Asegúrate de esperar la ejecución de la coroutine
        transaction = await generate_random_transfer(company_id, recurrent_clients, amount, is_anomalous)
        
        transactions.append(transaction)
    
    return transactions

# Insertar las transferencias en la base de datos
async def insert_transactions_to_db():
    companies_cursor = await db.companies.distinct("_id")  # Obtiene todos los ID de empresa únicos
    company_ids = [str(company_id) for company_id in companies_cursor]
    for cid in company_ids:
        transactions = await generate_transactions_for_company(cid)
        if transactions:  # Verifica que haya transacciones antes de insertar
            await transfers_collection.insert_many(transactions)  # Inserta las transferencias en la colección
        else:
            print(f"No se generaron transacciones para la empresa {cid}")

# Ejecutar la inserción
import asyncio
asyncio.run(insert_transactions_to_db())

