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

    # Listado de ciudades españolas
    spanish_cities = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Zaragoza", "Bilbao", "Málaga", "Murcia", "Palma", "Valladolid"]
    
    # Listado de ciudades internacionales
    international_cities = ["New York, USA", "London, UK", "Paris, France", "Berlin, Germany", "Tokyo, Japan",
                            "Shanghai, China", "Dubai, UAE", "São Paulo, Brazil", "Delhi, India", "Sydney, Australia"]

    # Mayor probabilidad de ciudades españolas en origen y destino
    if random.random() < 0.7:
        origin_location = random.choice(spanish_cities) + ", Spain"
    else:
        origin_location = random.choice(international_cities)

    if random.random() < 0.7:
        destination_location = random.choice(spanish_cities) + ", Spain"
    else:
        destination_location = random.choice(international_cities)

    # Métodos de pago
    payment_methods = [
        "tarjeta de crédito", "tarjeta de débito", "transferencia bancaria",
        "Bizum", "PayPal", "Stripe", "efectivo", "cripto (Bitcoin, Ethereum)"
    ]

    # Descripciones variadas
    descriptions = [
        "Pago de nómina", "Compra de mercancía", "Pago de factura", "Devolución de cliente",
        "Pago de alquiler", "Pago a proveedores", "Inversión financiera", "Gastos de viaje",
        "Reembolso de cliente", "Pago de impuestos", "Compra de software"
    ]

    # Categorías bancarias reales
    categories = [
        "alimentación", "ocio", "servicios", "ropa", "tecnología",
        "transporte", "salud", "hostelería", "educación", "inversión",
        "seguros", "hipoteca", "alquiler", "préstamos", "impuestos"
    ]

    # IBANs aleatorios
    def generate_iban():
        country_codes = ["ES", "US", "GB", "FR", "DE", "IT", "NL", "JP", "CN", "BR", "AE", "IN"]
        return f"{random.choice(country_codes)}{random.randint(10, 99)}{random.randint(1000, 9999)}{random.randint(1000000000, 9999999999)}"

    # Generación de IPs aleatorias simulando conexiones reales
    def generate_ip():
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"

    return {
        "id": str(uuid.uuid4()),  # ID único con UUID
        "amount": round(random.uniform(5, 50000), 2),  # Monto en EUR ya convertido
        "currency": "EUR",  # Siempre en euros
        "from_account": generate_iban(),  # IBAN origen
        "to_account": generate_iban(),  # IBAN destino
        "timestamp": datetime.utcnow().isoformat(),  # Fecha y hora en UTC
        "description": random.choice(descriptions),
        "category": random.choice(categories),
        "origin_location": origin_location,  # Mayor probabilidad de ser España
        "destination_location": destination_location,  # Mayor probabilidad de ser España
        "payment_method": random.choice(payment_methods),
        "status": random.choice(["completeda", "pendiente", "fallida"]),
        "user_identifier": f"user_{random.randint(1, 10000)}",
        "is_recurring": random.choice([True, False]),
        "device_fingerprint": f"device_{random.randint(1000, 9999)}",
        "client_ip": generate_ip(),  # IP más variada
        "company_id": str(company_id),
        "transaction_fee": round(random.uniform(0, 50), 2),  # Comisiones variadas
        "is_anomalous": False,  # Siempre False hasta que el modelo lo determine
        "linked_order_id": f"order_{random.randint(1, 5000)}"  # Más variedad de órdenes
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
