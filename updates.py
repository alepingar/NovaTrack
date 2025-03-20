from motor.motor_asyncio import AsyncIOMotorClient
from enum import Enum
from datetime import datetime, timezone
import asyncio

# Definir el Enum SubscriptionPlan
class SubscriptionPlan(str, Enum):
    BASICO = "Básico"
    NORMAL = "Normal"
    PRO = "Pro"

# Conectar con MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["nova_track"]
companies_collection = db["companies"]

async def insert_companies():
    companies = [
        {
            "name": "Spotify",
            "email": "spotify@example.com",
            "password": "$2b$12$dfdsf34ds2fdsf23sdfsd98df",
            "industry": "Música",
            "country": "Suecia",
            "phone_number": "555765432",
            "tax_id": "SE5566778899",
            "address": "Birger Jarlsgatan 61, Stockholm",
            "founded_date": datetime(2006, 10, 7, tzinfo=timezone.utc),
            "billing_account_number": "SE2323232323232323232323",
            "entity_type": "Corporación",
            "subscription_plan": SubscriptionPlan.PRO.value,
            "terms_accepted": True,
            "privacy_policy_accepted": True,
            "data_processing_consent": True,
            "communication_consent": False,
            "consent_timestamp": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "account_locked": False,
            "failed_login_attempts": 0,
            "last_login": datetime.now(timezone.utc),
            "account_deletion_requested": False,
            "data_sharing_consent": True,
        },
        {
            "name": "Samsung",
            "email": "samsung@example.com",
            "password": "$2b$12$slkdjfds8fhsdf98sd9fdlfjds",
            "industry": "Electrónica",
            "country": "Corea del Sur",
            "phone_number": "555222111",
            "tax_id": "KR1234567890",
            "address": "129, Samsung-ro, Yeongtong-gu, Suwon",
            "founded_date": datetime(1938, 3, 1, tzinfo=timezone.utc),
            "billing_account_number": "KR2323232323232323232323",
            "entity_type": "Corporación",
            "subscription_plan": SubscriptionPlan.NORMAL.value,
            "terms_accepted": True,
            "privacy_policy_accepted": True,
            "data_processing_consent": True,
            "communication_consent": True,
            "consent_timestamp": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "account_locked": False,
            "failed_login_attempts": 0,
            "last_login": datetime.now(timezone.utc),
            "account_deletion_requested": False,
            "data_sharing_consent": True,
        },
        {
            "name": "Adobe",
            "email": "adobe@example.com",
            "password": "$2b$12$hdgshf8s7dfj2sdsd8dsf7d3sd",
            "industry": "Software",
            "country": "Estados Unidos",
            "phone_number": "555444333",
            "tax_id": "US111223344",
            "address": "345 Park Avenue, San Jose, CA",
            "founded_date": datetime(1982, 12, 8, tzinfo=timezone.utc),
            "billing_account_number": "US2323232323232323232324",
            "entity_type": "Corporación",
            "subscription_plan": SubscriptionPlan.BASICO.value,
            "terms_accepted": True,
            "privacy_policy_accepted": True,
            "data_processing_consent": True,
            "communication_consent": False,
            "consent_timestamp": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "account_locked": False,
            "failed_login_attempts": 0,
            "last_login": datetime.now(timezone.utc),
            "account_deletion_requested": False,
            "data_sharing_consent": True,
        },
        {
            "name": "Nike",
            "email": "nike@example.com",
            "password": "$2b$12$jsdfldkfj83dkjfdfh4f2wfs8df",
            "industry": "Deportes",
            "country": "Estados Unidos",
            "phone_number": "555123456",
            "tax_id": "US222334455",
            "address": "One Bowerman Drive, Beaverton, OR",
            "founded_date": datetime(1964, 1, 25, tzinfo=timezone.utc),
            "billing_account_number": "US2323232323232323232325",
            "entity_type": "Corporación",
            "subscription_plan": SubscriptionPlan.PRO.value,
            "terms_accepted": True,
            "privacy_policy_accepted": True,
            "data_processing_consent": True,
            "communication_consent": True,
            "consent_timestamp": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "account_locked": False,
            "failed_login_attempts": 0,
            "last_login": datetime.now(timezone.utc),
            "account_deletion_requested": False,
            "data_sharing_consent": True,
        },
        {
            "name": "Uber",
            "email": "uber@example.com",
            "password": "$2b$12$sdjfg89dfsd7f8ds7f8sdf7sfj23",
            "industry": "Transporte",
            "country": "Estados Unidos",
            "phone_number": "555876987",
            "tax_id": "US556677889",
            "address": "1455 Market Street, San Francisco, CA",
            "founded_date": datetime(2009, 3, 1, tzinfo=timezone.utc),
            "billing_account_number": "US2323232323232323232326",
            "entity_type": "Corporación",
            "subscription_plan": SubscriptionPlan.NORMAL.value,
            "terms_accepted": True,
            "privacy_policy_accepted": True,
            "data_processing_consent": True,
            "communication_consent": False,
            "consent_timestamp": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "account_locked": False,
            "failed_login_attempts": 0,
            "last_login": datetime.now(timezone.utc),
            "account_deletion_requested": False,
            "data_sharing_consent": True,
        },
    ]

    # Insertar las compañías en la base de datos
    result = await companies_collection.insert_many(companies)
    print(f"✅ Compañías insertadas: {len(result.inserted_ids)}")

# Ejecutar la inserción de compañías
asyncio.run(insert_companies())
