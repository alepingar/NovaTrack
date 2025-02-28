from motor.motor_asyncio import AsyncIOMotorClient
import random
import uuid
from datetime import datetime, timedelta

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
def generate_iban_es():
    return f"ES{random.randint(10,99)} {random.randint(1000000000, 9999999999)}"

# Genera IBAN internacional válido (Ejemplo simple)
def generate_international_iban():
    # Diccionario de países y el número de dígitos del número de cuenta
    iban_format = {
        "FR": (2, 11),  # Francia: 2 dígitos de control + 11 dígitos de cuenta
        "DE": (2, 10),  # Alemania: 2 dígitos de control + 10 dígitos de cuenta
        "GB": (2, 8),   # Reino Unido: 2 dígitos de control + 8 dígitos de cuenta
        "IT": (2, 10),  # Italia: 2 dígitos de control + 10 dígitos de cuenta
        "US": (2, 10)   # Estados Unidos: 2 dígitos de control + 10 dígitos de cuenta
    }
    
    # Elegir un país al azar
    country_code = random.choice(list(iban_format.keys()))
    
    # Obtener el número de dígitos del número de cuenta según el país
    control_digits, account_digits = iban_format[country_code]
    
    # Generar el IBAN
    control_code = random.randint(10, 99)  # Generar el código de control
    account_number = random.randint(10**(account_digits-1), 10**account_digits - 1)  # Generar el número de cuenta
    
    # Formar el IBAN
    iban = f"{country_code}{control_digits}{control_code:02d}{account_number}"
    
    return iban

# Función para seleccionar el estado de la transferencia
def generate_status(is_anomalous):
    if is_anomalous:
        # Para las anomalías, más probabilidad de "fallida"
        return random.choices(["fallida", "completada", "pendiente"], weights=[70, 20, 10], k=1)[0]
    else:
        # Para las normales, más probabilidad de "completada"
        return random.choices(["completada", "pendiente", "fallida"], weights=[80, 10, 10], k=1)[0]

# Genera una transferencia aleatoria
def generate_random_transfer(company_id, avg_amount, is_anomalous=False):
    # Definir el rango de los montos, con una distribución alrededor del promedio
    amount = round(random.uniform(avg_amount * 0.5, avg_amount * 1.5), 2)
    
    # Generar fecha de transferencia aleatoria (más frecuente en las anomalías)
    days_ago = random.randint(1, 60)  # Aleatorio entre 1 y 60 días atrás
    hours_ago = random.randint(0, 23)  # Aleatorio entre 0 y 23 horas
    minutes_ago = random.randint(0, 59)  # Aleatorio entre 0 y 59 minutos
    seconds_ago = random.randint(0, 59)  # Aleatorio entre 0 y 59 segundos
    
    # Crear el timestamp final con la variabilidad en días, horas, minutos y segundos
    timestamp = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago, seconds=seconds_ago)
    
    # Si es anómala, podemos cambiar el monto
    if is_anomalous:
        # Monto exageradamente alto o bajo
        anomaly_type = random.choice(["high", "low"])
        
        if anomaly_type == "high":
            # Monto exageradamente alto
            amount = round(random.uniform(avg_amount * 2, avg_amount * 5), 2)
        else:
            # Monto exageradamente bajo
            amount = round(random.uniform(0, avg_amount * 0.3), 2)
    
    # Decidir IBAN de destino: puede ser español o internacional (con probabilidad ajustada)
    from_account = generate_international_iban() if random.random() > 0.8 else generate_iban_es()
    to_account = "ES2071549200121562384309"  # 80% de probabilidad de ser un IBAN español
    
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
        "timestamp": timestamp.isoformat(),  # Fecha aleatoria dentro del mes pasado
        "status": status,
        "company_id": str(company_id),
        "is_anomalous": is_anomalous,
    }

# Generar las transferencias para una empresa, con anomalías controladas
def generate_transactions_for_company(company_id, avg_amount, num_transactions=100):
    transactions = []
    
    # Determinar cuántas transferencias serán anómalas (entre 1 y 10% de las transferencias)
    num_anomalous = random.randint(num_transactions // 100, num_transactions // 10)  # Entre 1 y 10 transferencias anómalas

    # Generar las transferencias
    for i in range(num_transactions):
        is_anomalous = i < num_anomalous  # Las primeras "num_anomalous" serán anómalas
        transactions.append(generate_random_transfer(company_id, avg_amount, is_anomalous))
    
    return transactions

# Conexión a la base de datos MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
transfers_collection = db["transfers"]

# Ejemplo de generación de datos
company_id = "678e8959a2f4f54c5d481ba1"  # Aquí colocarías el ID de una empresa de tu base de datos
avg_amount = 37  # Definir un monto promedio para las transferencias
transactions = generate_transactions_for_company(company_id, avg_amount)

# Insertar las transferencias en la base de datos
async def insert_transactions_to_db():
    await transfers_collection.insert_many(transactions)  # Inserta las transferencias en la colección

# Ejecutar la inserción
import asyncio
asyncio.run(insert_transactions_to_db())

# Verificar el resultado
for t in transactions:
    print(f"Transferencia {t['id']} - Monto: {t['amount']} {t['currency']} - Estado: {t['status']} - Anómala: {t['is_anomalous']}")
