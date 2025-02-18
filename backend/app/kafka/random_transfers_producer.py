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
    Ajustada para reflejar los campos del modelo Transfer.
    """
    return {
        "id": random.randint(1, 10000),
        "amount": round(random.uniform(10, 5000), 2),  # 'monto' a 'amount'
        "currency": random.choice(["USD", "EUR", "GBP"]),  # 'moneda' a 'currency'
        "from_account": f"Cuenta_{random.randint(1000000000, 9999999999)}",  # 'cuenta_origen' a 'from_account'
        "to_account": f"Cuenta_{random.randint(1000000000, 9999999999)}",  # 'cuenta_destino' a 'to_account'
        "timestamp": datetime.utcnow().isoformat(),  # 'fecha_hora' a 'timestamp'
        "description": random.choice(["Compra", "Pago de servicios", "Transferencia interna"]),  # 'descripcion' a 'description'
        "category": random.choice(["servicios", "supermercado", "entretenimiento"]),  # 'categoria' a 'category'
        "origin_location": random.choice(["New York, USA", "Los Angeles, USA", "London, UK"]),  # 'ubicacion_origen' a 'origin_location'
        "destination_location": random.choice(["Paris, France", "Berlin, Germany", "Madrid, Spain"]),  # 'ubicacion_destino' a 'destination_location'
        "payment_method": random.choice(["credit_card", "bank_transfer", "cash"]),  # 'metodo_pago' a 'payment_method'
        "status": random.choice(["completed", "pending", "failed"]),  # 'estado' a 'status'
        "user_identifier": f"user_{random.randint(1, 100)}",  # 'identificador_usuario' a 'user_identifier'
        "is_recurring": random.choice([True, False]),  # 'es_recurrente' a 'is_recurring'
        "device_fingerprint": f"device_{random.randint(1000, 9999)}",  # 'huella_dispositivo' a 'device_fingerprint'
        "client_ip": f"192.168.1.{random.randint(1, 255)}",  # 'ip_cliente' a 'client_ip'
        "company_id": str(company_id),  # 'id_empresa' a 'company_id'
        "transaction_fee": round(random.uniform(0, 20), 2),  # 'tarifa_transaccion' a 'transaction_fee'
        "is_anomalous": random.choice([True, False]),  # 'es_anomala' a 'is_anomalous'
        "linked_order_id": (f"order_{random.randint(1, 500)}" if random.random() > 0.5 else None)  # 'id_pedido_relacionado' a 'linked_order_id'
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
