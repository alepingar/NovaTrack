import time
import random
import uuid
import json
from datetime import datetime
from confluent_kafka import Producer
from pymongo import MongoClient

# Configuración del productor
producer_config = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(producer_config)

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["nova_track"]

def get_companies():
    """
    Obtiene todas las empresas desde la base de datos.
    """
    return list(db.companies.find({}, {"_id": 1, "name": 1}))

def generate_random_transfer(company_id):
    """
    Genera una transferencia aleatoria para una empresa española con transferencias nacionales e internacionales,
    considerando que la empresa ve todas las transferencias en EUR.
    """
    # IBANs aleatorios
    def generate_iban():
        country_codes = ["ES", "US", "GB", "FR", "DE", "IT", "NL", "JP", "CN", "BR", "AE", "IN"]
        return f"{random.choice(country_codes)}{random.randint(10, 99)}{random.randint(1000, 9999)}{random.randint(1000000000, 9999999999)}"

    return {
        "id": str(uuid.uuid4()),  # ID único con UUID
        "amount": round(random.uniform(5, 10000), 2),  # Monto en EUR ya convertido
        "currency": "EUR",  # Siempre en euros
        "from_account": generate_iban(),
        "to_account": generate_iban(), # IBAN origen
        "timestamp": datetime.utcnow().isoformat(),  # Fecha y hora en UTC
        "status": random.choice(["completada", "pendiente", "fallida"]),
        "company_id": str(company_id),
        "is_anomalous": False,  # Siempre False hasta que el modelo lo determine
    }

def produce_continuous_transfers():
    """
    Produce transferencias aleatorias asociadas a empresas existentes de forma continua.
    """
    companies = get_companies()
    if not companies:
        print("No hay empresas en la base de datos. Agrega empresas antes de ejecutar el productor.")
        return

    print(f"Empresas encontradas: {[company['name'] for company in companies]}")
    try:
        while True:
            company = random.choice(companies)
            transfer = generate_random_transfer(company["_id"])
            producer.produce(
                'transfers',
                key=str(transfer["id"]),
                value=json.dumps(transfer, ensure_ascii=False)
            )
            producer.flush()
            print(f"Transferencia enviada para {company['name']}: {transfer}")
            
            time.sleep(random.uniform(40, 120))  
    except KeyboardInterrupt:
        print("\nGeneración de transferencias interrumpida.")
    finally:
        producer.flush()

if __name__ == "__main__":
    produce_continuous_transfers()
