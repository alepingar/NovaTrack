#!/usr/bin/env python3
import asyncio
from enum import Enum
import os
import random
import sys 
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional 
from passlib.context import CryptContext
import numpy as np
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

# --- CONFIGURACIÓN GENERAL ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "nova_track"
COMPANIES_COLLECTION_NAME = "companies"
TRANSFERS_COLLECTION_NAME = "transfers"

class SubscriptionPlan(str, Enum): # Puedes renombrarlo si quieres, ej. PopulatorSubscriptionPlan
    BASICO = "BASICO"
    PRO = "PRO"
    # Añade aquí todos los miembros de tu Enum SubscriptionPlan original

class EntityType(str, Enum): # Puedes renombrarlo si quieres, ej. PopulatorEntityType
    SA = "Sociedad Anónima"
    SL = "Sociedad Limitada"
    SLNE = "Sociedad Limitada Nueva Empresa"
    AUTONOMO = "Autónomo"
    COOPERATIVA = "Sociedad Cooperativa"
    SOCIEDAD_CIVIL = "Sociedad Civil"
    COMUNIDAD_BIENES = "Comunidad de Bienes"
    ENTIDAD_PUBLICA = "Entidad Pública"
    ASOCIACION = "Asociación"
    FUNDACION = "Fundación"
    OTRO = "Otro"
    
# --- CONFIGURACIÓN PARA LA EMPRESA DE PRUEBA DEL TFG ---
TFG_COMPANY_NAME = "NovaTrack"
TFG_COMPANY_EMAIL = "ceo@novatrack.com"
TFG_COMPANY_PASSWORD_PLAIN = "Str0ngP@ssw0rd!" 
TFG_COMPANY_INDUSTRY = "Software de Seguimiento Financiero"
TFG_COMPANY_COUNTRY = "España"
TFG_COMPANY_PHONE = "+34600112233"
TFG_COMPANY_TAX_ID = "B12345678" 
TFG_COMPANY_ADDRESS = "Calle Ficticia 123, 28080 Madrid"
TFG_COMPANY_FOUNDED_DATE = datetime(2022, 1, 15, tzinfo=timezone.utc)
TFG_COMPANY_BILLING_ACCOUNT = "ES6000491234567890123456" 

TFG_COMPANY_ENTITY_TYPE = EntityType.SL.value
TFG_COMPANY_SUBSCRIPTION_PLAN = SubscriptionPlan.BASICO.value

NUM_TRANSFERS_FOR_TFG_COMPANY = 750  
AVG_AMOUNT_TFG_COMPANY = 350.0      


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BANCOS_ESP = [
    "0049", "0075", "0081", "2100", "0182", "1465", "0128", "2038",
]

def generate_iban_es():
    country_code = "ES"
    check_digits = f"{random.randint(10, 99):02d}"
    bank_code = random.choice(BANCOS_ESP)
    branch_code = f"{random.randint(1000, 9999):04d}"
    account_number = f"{random.randint(0, 999999999999):012d}"
    return f"{country_code}{check_digits}{bank_code}{branch_code}{account_number}"

def generate_recurrent_clients(num_clients):
    return [generate_iban_es() for _ in range(num_clients)]

def generate_status(is_anomalous):
    if is_anomalous:
        return random.choices(["completada", "fallida", "pendiente"], weights=[0.70, 0.20, 0.10], k=1)[0]
    else:
        return random.choices(["completada", "pendiente", "fallida"], weights=[0.98, 0.01, 0.01], k=1)[0]

async def generate_random_transfer_for_tfg(
    company_id_str: str,
    company_billing_account: str, 
    recurrent_clients: List[str],
    avg_amount: float,
    is_anomalous: bool = False
):
    MIN_AMOUNT = 3.00
    MAX_AMOUNT = avg_amount * 10
    if is_anomalous:
        random_value = random.random()
        if random_value < 0.80:
            if random.random() > 0.5: amount = round(random.lognormvariate(np.log(avg_amount * 4), 0.6), 2)
            else: amount = round(random.uniform(MIN_AMOUNT, avg_amount * 0.2), 2)
        elif random_value < 0.90: amount = round(random.uniform(avg_amount * 0.5, avg_amount * 1.5), 2)
        else: amount = round(random.gauss(avg_amount, avg_amount * 0.2), 2)
    else:
        random_value = random.random()
        if random_value < 0.80: amount = round(random.gauss(avg_amount, avg_amount * 0.25), 2)
        elif random_value < 0.90: amount = round(random.uniform(avg_amount * 0.7, avg_amount * 1.7), 2)
        else: amount = round(random.uniform(avg_amount * 0.4, avg_amount * 2.5), 2)
    amount = max(MIN_AMOUNT, min(amount, MAX_AMOUNT))
    today = datetime.now(timezone.utc)
    days_ago = random.randint(1, 365)
    date_base = today - timedelta(days=days_ago)
    if is_anomalous:
        hours_population = list(range(0, 8)) + list(range(8, 22)) + list(range(22, 24))
        hours_weights = [0.3/8]*8 + [0.4/14]*14 + [0.3/2]*2 
    else:
        hours_population = list(range(8, 22)) + list(range(0, 8)) + list(range(22, 24))
        hours_weights = [0.9/14]*14 + [0.05/8]*8 + [0.05/2]*2 
    hours_weights_sum = sum(hours_weights)
    normalized_hours_weights = [w / hours_weights_sum for w in hours_weights]
    hours_ago = random.choices(population=hours_population, weights=normalized_hours_weights, k=1)[0]
    minutes_ago = random.randint(0, 59)
    seconds_ago = random.randint(0, 59)
    timestamp = datetime(
        date_base.year, date_base.month, date_base.day,
        hours_ago, minutes_ago, seconds_ago, tzinfo=timezone.utc
    )
    if is_anomalous: use_recurrent = random.choices([True, False], weights=[0.30, 0.70])[0]
    else: use_recurrent = random.choices([True, False], weights=[0.80, 0.20])[0]
    from_account = random.choice(recurrent_clients) if use_recurrent and recurrent_clients else generate_iban_es()
    to_account = company_billing_account
    currency = "EUR"
    status_val = generate_status(is_anomalous) 
    return {
        "id": str(uuid.uuid4()), 
        "amount": amount,
        "currency": currency,
        "from_account": from_account,
        "to_account": to_account,
        "timestamp": timestamp,
        "status": status_val, 
        "company_id": company_id_str, 
        "is_anomalous": is_anomalous,
        "created_at": datetime.now(timezone.utc), 
        "updated_at": datetime.now(timezone.utc), 
    }

async def populate_transfers_for_tfg_company(
    db_transfers_collection: AsyncIOMotorClient, 
    company_id_obj: ObjectId,
    company_billing_account: str,
    num_total_transfers: int,
    avg_amount_for_company: float
):
    print(f"\nGenerando {num_total_transfers} transferencias para la empresa TFG (ID: {str(company_id_obj)})...")
    num_recurrent_clients = random.randint(40, 120) 
    recurrent_clients_list = generate_recurrent_clients(num_recurrent_clients)
    target_anomaly_rate = 0.075 
    num_anomalous_target = int(target_anomaly_rate * num_total_transfers)
    print(f"  Objetivo: ~{num_anomalous_target} transferencias anómalas.")
    generated_transfers = []
    anomalies_count = 0
    for i in range(num_total_transfers):
        is_current_transfer_anomalous = False
        if anomalies_count < num_anomalous_target:
            if random.random() < (num_anomalous_target - anomalies_count) / max(1, (num_total_transfers - i)):
                 is_current_transfer_anomalous = True
        if not is_current_transfer_anomalous:
            is_current_transfer_anomalous = random.random() < (target_anomaly_rate * 0.5) 
        if is_current_transfer_anomalous:
            anomalies_count += 1
        transfer_doc = await generate_random_transfer_for_tfg(
            str(company_id_obj), 
            company_billing_account,
            recurrent_clients_list,
            avg_amount_for_company,
            is_current_transfer_anomalous
        )
        generated_transfers.append(transfer_doc)
        if (i + 1) % 100 == 0:
            print(f"  ... {i+1}/{num_total_transfers} transferencias generadas ({anomalies_count} anómalas hasta ahora)")
    if generated_transfers:
        print(f"\nInsertando {len(generated_transfers)} transferencias en la base de datos...")
        try:
     
            await db_transfers_collection.insert_many(generated_transfers, ordered=False) 
            print(f"¡Éxito! {len(generated_transfers)} transferencias insertadas.")
            print(f"Total de transferencias anómalas generadas: {anomalies_count}")
        except Exception as e:
            print(f"Error masivo al insertar transferencias: {e}")

            raise 
    else:
        print("No se generaron transferencias para insertar.")


async def create_or_get_tfg_company(db_companies_collection: AsyncIOMotorClient) -> tuple[Optional[ObjectId], Optional[str]]:
    """Crea la empresa TFG si no existe, o devuelve el ID de la existente.
       Ahora guardará la contraseña hasheada correctamente."""
    print(f"Buscando empresa TFG con email: {TFG_COMPANY_EMAIL}...")
    existing_company = await db_companies_collection.find_one({"email": TFG_COMPANY_EMAIL.lower()})
    
    if existing_company:
        print(f"Empresa TFG encontrada con ID: {existing_company['_id']}.")
        if existing_company.get("billing_account_number") != TFG_COMPANY_BILLING_ACCOUNT:
            print(f"  ADVERTENCIA: El IBAN en BBDD ({existing_company.get('billing_account_number')}) "
                  f"difiere del configurado ({TFG_COMPANY_BILLING_ACCOUNT}). Usando el de BBDD.")
        return existing_company['_id'], existing_company.get("billing_account_number", TFG_COMPANY_BILLING_ACCOUNT)

    print(f"Empresa TFG no encontrada. Creando '{TFG_COMPANY_NAME}'...")
    

    real_hashed_password = pwd_context.hash(TFG_COMPANY_PASSWORD_PLAIN) 

    company_document = {
        "name": TFG_COMPANY_NAME,
        "email": TFG_COMPANY_EMAIL.lower(),
        "password": real_hashed_password, 
        "industry": TFG_COMPANY_INDUSTRY,
        "country": TFG_COMPANY_COUNTRY,
        "phone_number": TFG_COMPANY_PHONE,
        "tax_id": TFG_COMPANY_TAX_ID,
        "address": TFG_COMPANY_ADDRESS,
        "founded_date": TFG_COMPANY_FOUNDED_DATE,
        "billing_account_number": TFG_COMPANY_BILLING_ACCOUNT,
        "entity_type": TFG_COMPANY_ENTITY_TYPE,
        "subscription_plan": TFG_COMPANY_SUBSCRIPTION_PLAN,
        "terms_accepted": True,
        "privacy_policy_accepted": True,
        "data_processing_consent": True,
        "communication_consent": True,
        "consent_timestamp": datetime.now(timezone.utc), 
        "uploads_count": 0,
        "last_login": datetime.now(timezone.utc) - timedelta(hours=random.randint(1,24)),
        "failed_login_attempts": 0,
        "account_locked": False,
        "gdpr_request_log": [],
        "account_deletion_requested": False,
        "data_sharing_consent": True,
        "created_at": datetime.now(timezone.utc), 
        "updated_at": datetime.now(timezone.utc), 
    }

    try:
        result = await db_companies_collection.insert_one(company_document)
        new_company_id = result.inserted_id
        print(f"Empresa TFG '{TFG_COMPANY_NAME}' creada con éxito. ID: {new_company_id} (Contraseña hasheada)")
        return new_company_id, TFG_COMPANY_BILLING_ACCOUNT
    except DuplicateKeyError:
        print(f"Error: Fallo al insertar la empresa. ¿Quizás un 'tax_id' duplicado? ({TFG_COMPANY_TAX_ID})")
        print("Intentando recuperar por tax_id si el email falló...")
        existing_company_by_tax = await db_companies_collection.find_one({"tax_id": TFG_COMPANY_TAX_ID})
        if existing_company_by_tax:
            print(f"Empresa encontrada por tax_id: {existing_company_by_tax['_id']}")
            return existing_company_by_tax['_id'], existing_company_by_tax.get("billing_account_number", TFG_COMPANY_BILLING_ACCOUNT)
        raise 
    except Exception as e:
        print(f"Error inesperado al crear la empresa TFG: {e}")
        raise

async def run_population():
    print("--- Iniciando script de población de datos para TFG ---")
    
    client = None 
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        await client.admin.command('ping') 
        print(f"Conexión a MongoDB en {MONGO_URI} exitosa.")

        db = client[DB_NAME]
        companies_collection_instance = db[COMPANIES_COLLECTION_NAME]
        transfers_collection_instance = db[TRANSFERS_COLLECTION_NAME]
        population_markers_collection = db["_app_markers"]
        
        marker_id = "tfg_initial_data_populated_v1"
        existing_marker = await population_markers_collection.find_one({"_id": marker_id})
        
        if existing_marker:
            print(f"Marcador '{marker_id}' encontrado. La base de datos ya fue poblada anteriormente. Saltando script.")
            return
        
        print(f"Marcador '{marker_id}' no encontrado. Procediendo con la población de datos...")

        company_id, company_iban = await create_or_get_tfg_company(companies_collection_instance)
        
        if not company_id or not company_iban:
            print("Error crítico: No se pudo crear o recuperar la empresa TFG. Abortando.")
            raise Exception("Fallo en create_or_get_tfg_company sin una excepción previa.")

        print(f"Limpiando transferencias antiguas (si existen) para la empresa ID: {company_id}...")
        del_result = await transfers_collection_instance.delete_many({"company_id": str(company_id)})
        print(f"Eliminadas {del_result.deleted_count} transferencias antiguas para la empresa TFG.")

        await populate_transfers_for_tfg_company(
            transfers_collection_instance,
            company_id, 
            company_iban,
            NUM_TRANSFERS_FOR_TFG_COMPANY,
            AVG_AMOUNT_TFG_COMPANY
        )
        
        await population_markers_collection.insert_one({
            "_id": marker_id, 
            "description": "Indica que los datos iniciales del TFG han sido poblados.",
            "timestamp": datetime.now(timezone.utc) 
        })
        print(f"Marcador '{marker_id}' guardado en la base de datos.")
        print("\n--- Proceso de población de datos para TFG completado con éxito. ---")

    except Exception as e:
        print(f"ERROR FATAL durante el proceso de población: {e}")
        raise
    finally:
        if client:
            client.close()
            print("Conexión a MongoDB cerrada.")


if __name__ == "__main__":
    print(f"Ejecutando script de población: {__file__}")
    print(f"Intentando conectar a MongoDB en: {MONGO_URI}")
    try:
        asyncio.run(run_population())

        print("Script de población finalizado con éxito.")
        sys.exit(0)
    except Exception as e:
  
        print(f"El script de población falló: {e}")
        sys.exit(1) 