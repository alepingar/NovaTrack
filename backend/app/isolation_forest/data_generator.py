from motor.motor_asyncio import AsyncIOMotorClient
import random
import uuid
from datetime import datetime, timedelta, timezone
from bson import ObjectId
# Diccionario de monedas por país
currency_by_country = {
    "ES": "EUR",  # España -> Euro
    "FR": "EUR",  # Francia -> Euro
    "DE": "EUR",  # Alemania -> Euro
    "GB": "GBP",  # Reino Unido -> Libra
    "US": "USD",  # Estados Unidos -> Dólar
    # Puedes agregar más países y monedas según sea necesario
}

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
    amount = round(random.uniform(avg_amount * 0.5, avg_amount * 1.5), 2)
    
    # Generar fecha de transferencia aleatoria (más frecuente en las anomalías)
    days_ago = random.randint(3, 63)  # Aleatorio entre 3 y 63 días atrás
    minutes_ago = random.randint(0, 59)  # Aleatorio entre 0 y 59 minutos
    seconds_ago = random.randint(0, 59)  # Aleatorio entre 0 y 59 segundos
    
    # Crear el timestamp final con la variabilidad en días, horas, minutos y segundos
    if is_anomalous:
    # Mayor probabilidad de horarios fuera del horario bancario (22:00 - 08:00)
        hours_ago = random.choices(
            population=list(range(0, 8)) + list(range(22, 24)),  # Horas anómalas
            weights=[0.4] * 8 + [0.6] * 2,  # Probabilidad mayor entre 22:00 y 08:00
            k=1
        )[0]
    else:
    # Mayor probabilidad de horarios bancarios (08:00 - 22:00)
        hours_ago = random.choices(
            population=list(range(8, 22)),  # Horas normales
            weights=[1] * 14,  # Probabilidad uniforme entre 08:00 y 22:00
            k=1
        )[0]

    # Crear el timestamp final con la variabilidad en días, horas, minutos y segundos
    timestamp = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago, seconds=seconds_ago)
    
    # Si es anómala, podemos cambiar el monto
    if is_anomalous:
        # Monto exageradamente alto o bajo
        anomaly_type = random.choice(["high", "low"])
        
        if anomaly_type == "high":
            # Monto exageradamente alto, con una distribución log-normal (media mucho mayor, desviación moderada)
            amount = round(random.lognormvariate(avg_amount * 5, 0.5), 2)  # Factor *5 para monto más grande
            amount = min(amount, 1000)
        else:
            # Monto exageradamente bajo, con una distribución log-normal (media pequeña, desviación moderada)
            amount = round(random.lognormvariate(avg_amount * 0.05, 0.5), 2)
            amount = max(amount, 0.5)
    
    # Decidir IBAN de destino: puede ser español o internacional (con probabilidad ajustada)
    use_recurrent = random.choices([True, False], weights=[80, 20])[0]  # 80% recurrente, 20% nuevo
    
    if use_recurrent:
        from_account = random.choice(recurrent_clients)  # Cliente conocido
    else:
        from_account = generate_iban_es()  # Nuevo remitente
    
    to_account = await get_billing_account_company(company_id)  # 80% de probabilidad de ser un IBAN español
    # Obtener la moneda del país de destino
    to_country_code = from_account[:2]  # Los primeros dos caracteres del IBAN son el código del país
    currency = currency_by_country.get(to_country_code, "EUR")  # Si no está en el diccionario, por defecto EUR
    
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

