from motor.motor_asyncio import AsyncIOMotorClient
import random
import uuid
from datetime import datetime, timedelta, timezone
from bson import ObjectId
import numpy as np

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
def generate_recurrent_clients(num_clients=10):
    return [generate_iban_es() for _ in range(num_clients)]

# Función para seleccionar el estado de la transferencia
def generate_status(is_anomalous):
    if is_anomalous:
        # Para las anomalías, más probabilidad de "fallida"
        return random.choices(["fallida", "completada", "pendiente"], weights=[70, 20, 10], k=1)[0]
    else:
        # Para las normales, más probabilidad de "completada"
        return random.choices(["completada", "pendiente", "fallida"], weights=[80, 10, 10], k=1)[0]

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
    first_day_of_year = datetime(datetime.now().year, 1, 1, tzinfo=timezone.utc)

    # Calcular cuántos días han pasado desde el primer día del año hasta hoy
    days_since_first_day = (datetime.now(timezone.utc) - first_day_of_year).days

    # Ponderaciones para que las anomalías sean más frecuentes los fines de semana
    weekend_weight_anomalous = 0.5  
    weekday_weight_anomalous = 0.5  

    # Ponderaciones para transferencias normales (menos probabilidad en fines de semana)
    weekend_weight_normal = 0.2  
    weekday_weight_normal = 0.8  

    # Seleccionar un día aleatorio con más peso en fines de semana para anomalías
    if is_anomalous:
        days_ago = random.choices(
            population=range(3, days_since_first_day),  
            weights=[weekend_weight_anomalous if (datetime.now(timezone.utc) - timedelta(days=x)).weekday() in [5, 6] 
                    else weekday_weight_anomalous for x in range(3, days_since_first_day)],  
            k=1
        )[0]
    else:
        days_ago = random.choices(
            population=range(3, days_since_first_day),  
            weights=[weekend_weight_normal if (datetime.now(timezone.utc) - timedelta(days=x)).weekday() in [5, 6] 
                    else weekday_weight_normal for x in range(3, days_since_first_day)],  
            k=1
        )[0]

    # Generar la hora 
    minutes_ago = random.randint(0, 59)  
    seconds_ago = random.randint(0, 59)  

    if is_anomalous:
        hours_ago = random.choices(
            population=list(range(0, 8)) + list(range(8, 22)) + list(range(22, 24)),
            weights=[0.55] * 8 + [0.05] * 14 + [0.4] * 2,  
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
    
    # Decidir IBAN de destino: puede ser español o internacional (con probabilidad ajustada)
    use_recurrent = random.choices([True, False], weights=[80, 20])[0]  # 80% recurrente, 20% nuevo
    
    if use_recurrent:
        from_account = random.choice(recurrent_clients)  # Cliente conocido
    else:
        from_account = generate_iban_es()  # Nuevo remitente
    
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
        "timestamp": timestamp,  # Fecha aleatoria dentro del mes pasado
        "status": status,
        "company_id": str(company_id),
        "is_anomalous": is_anomalous,
    }

# Generar las transferencias para una empresa, con anomalías controladas
async def generate_transactions_for_company(company_id, avg_amount, num_transactions=1000):
    transactions = []
    
    # Determinar cuántas transferencias serán anómalas (entre 1 y 10% de las transferencias)
    num_anomalous = random.randint(num_transactions // 100, num_transactions // 10) 
    recurrent_clients = generate_recurrent_clients(200)
    
    # Generar las transferencias
    for i in range(num_transactions):
        is_anomalous = i < num_anomalous  # Las primeras "num_anomalous" serán anómalas
        
        # Asegúrate de esperar la ejecución de la coroutine
        transaction = await generate_random_transfer(company_id, recurrent_clients, avg_amount, is_anomalous)
        
        # Añadir la transferencia ya resuelta (no la coroutine)
        transactions.append(transaction)
    
    return transactions

# Conexión a la base de datos MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
transfers_collection = db["transfers"]

# Insertar las transferencias en la base de datos
async def insert_transactions_to_db():
    companies_cursor = await db.companies.distinct("_id")  # Obtiene todos los ID de empresa únicos
    company_ids = [str(company_id) for company_id in companies_cursor]
    for cid in company_ids:
        avg_amount = random.choice([10, 20, 30, 40, 50])  # Monto promedio aleatorio
        transactions = await generate_transactions_for_company(cid, avg_amount)
        if transactions:  # Verifica que haya transacciones antes de insertar
            await transfers_collection.insert_many(transactions)  # Inserta las transferencias en la colección
        else:
            print(f"No se generaron transacciones para la empresa {cid}")

# Ejecutar la inserción
import asyncio
asyncio.run(insert_transactions_to_db())

