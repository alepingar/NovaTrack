import time
import random
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
    Genera una transferencia aleatoria asociada a una empresa.
    """
    return {
        "id": random.randint(1, 10000),
        "amount": round(random.uniform(10, 5000), 2),
        "currency": random.choice(["USD", "EUR", "GBP"]),
        "from_account": f"Cuenta_{random.randint(1, 100)}",
        "to_account": f"Cuenta_{random.randint(1, 100)}",
        "timestamp": datetime.utcnow().isoformat(),
        "description": random.choice(["Compra", "Pago de servicios", "Transferencia interna"]),
        "category": random.choice(["utilities", "groceries", "entertainment"]),
        "origin_location": random.choice(["New York, USA", "Los Angeles, USA", "London, UK"]),
        "destination_location": random.choice(["Paris, France", "Berlin, Germany", "Madrid, Spain"]),
        "payment_method": random.choice(["credit_card", "bank_transfer", "cash"]),
        "status": random.choice(["completed", "pending", "failed"]),
        "user_id": f"user_{random.randint(1, 100)}",
        "recurring": random.choice([True, False]),
        "client_ip": f"192.168.1.{random.randint(1, 255)}",
        "company_id": str(company_id),  
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
                value=json.dumps(transfer)
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
