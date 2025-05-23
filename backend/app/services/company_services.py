from app.database import db
from app.models.company import CompanyResponse, CompanyCreate, UpdateCompanyProfile, EntityType, SubscriptionPlan
from bson import ObjectId
from fastapi import HTTPException
from app.utils.security import hash_password
from datetime import datetime, timedelta
from typing import List
import stripe
import os
from pymongo import ReturnDocument

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

async def fetch_companies() -> List[CompanyResponse]:
    """
    Obtiene todas las empresas registradas.
    """
    companies = await db.companies.find().to_list(length=None)
    return [
        CompanyResponse(
            id=str(company["_id"]),
            name=company["name"],
            email=company["email"],
            industry=company.get("industry"),
            country=company.get("country"),   
            created_at=company.get("created_at"),  
            updated_at=company.get("updated_at"),
        )
        for company in companies
    ]

async def register_new_company(company: CompanyCreate) -> CompanyResponse:
    """
    Registra una nueva empresa.
    """
    if not company.terms_accepted or not company.privacy_policy_accepted or not company.data_processing_consent:
        raise HTTPException(status_code=400, detail="Debes aceptar los términos y condiciones,la política de privacidad y el procesamiento de datos")
    
    if company.password != company.confirm_password:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")
    
    existing_company = await db.companies.find_one({"email": company.email})
    if existing_company:
        raise HTTPException(status_code=400, detail="La empresa ya está registrada")
    
    hashed_password = hash_password(company.password)

    company_data = company.dict()
    company_data.pop("confirm_password")
    company_data.update({
        "password": hashed_password,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "consent_timestamp": datetime.utcnow().isoformat(),
    })

    result = await db.companies.insert_one(company_data)

    return CompanyResponse(
        id=str(result.inserted_id),
        name=company.name,
        email=company.email,
        industry=company.industry,
        country=company.country,
        phone_number=company.phone_number,
        tax_id=company.tax_id,
        address=company.address,
        founded_date=company.founded_date,
        created_at=company_data["created_at"],
        updated_at=company_data["updated_at"],
        billing_account_number=company.billing_account_number
    )

async def fetch_company_profile(company_id: str) -> CompanyResponse:
    """
    Obtiene el perfil de una empresa por su ID.
    """
    company = await db.companies.find_one({"_id": ObjectId(company_id)})
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    return CompanyResponse(
        id=str(company["_id"]),
        name=company["name"],
        email=company["email"],
        industry=company.get("industry"),
        country=company.get("country"),
        phone_number=company.get("phone_number"),
        tax_id=company.get("tax_id"),
        address=company.get("address"),
        founded_date=company.get("founded_date"),
        created_at=company.get("created_at"),
        updated_at=company.get("updated_at"),
        billing_account_number=company.get("billing_account_number"),
        subscription_plan=company.get("subscription_plan"),
    )

async def update_company_profile(company_id: str, company_data: UpdateCompanyProfile) -> CompanyResponse:
    """
    Actualiza el perfil de una empresa.
    """
    # Verificar si la empresa existe
    existing_company = await db.companies.find_one({"_id": ObjectId(company_id)})
    if not existing_company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    # Convertir el objeto Pydantic a un diccionario
    updated_data = company_data.dict(exclude_unset=True)
    updated_data["updated_at"] = datetime.utcnow().isoformat()

    # Actualizar los datos en la base de datos
    await db.companies.update_one({"_id": ObjectId(company_id)}, {"$set": updated_data})

    # Recuperar los datos actualizados
    updated_company = await db.companies.find_one({"_id": ObjectId(company_id)})
    if not updated_company:
        raise HTTPException(status_code=500, detail="Error al recuperar los datos actualizados")

    # Retornar el objeto de respuesta
    return CompanyResponse(
        id=str(updated_company["_id"]),
        name=updated_company.get("name"),
        email=updated_company.get("email"),
        industry=updated_company.get("industry"),
        country=updated_company.get("country"),
        phone_number=updated_company.get("phone_number"),
        tax_id=updated_company.get("tax_id"),
        address=updated_company.get("address"),
        founded_date=updated_company.get("founded_date"),
        created_at=updated_company.get("created_at"),
        updated_at=updated_company.get("updated_at")
    )


async def get_entity_types1() -> List[EntityType]:
    return [entity for entity in EntityType]


async def get_current_plan(company_id: str) -> str:
    company = await db.companies.find_one({"_id": ObjectId(company_id)})
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    return company.get("subscription_plan", 0)


async def request_gdpr_action(company_id: str, action: str):
    """
    Registra una solicitud GDPR (acceso/eliminación de datos).
    """
    update_result = await db.companies.update_one(
        {"_id": ObjectId(company_id)},
        {"$push": {"gdpr_request_log": {"action": action}}}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=400, detail="No se pudo registrar la solicitud GDPR")
    
async def request_account_deletion(company_id: str):
    """
    Marca una empresa como que ha solicitado eliminación de cuenta.
    """
    update_result = await db.companies.update_one(
        {"_id": ObjectId(company_id)},
        {"$set": {"account_deletion_requested": True}}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=400, detail="No se pudo solicitar la eliminación de cuenta")


async def update_data_sharing_consent(company_id: str, consent: bool):
    """
    Actualiza el consentimiento de compartir datos de la empresa.
    """
    update_result = await db.companies.update_one(
        {"_id": ObjectId(company_id)},
        {"$set": {"data_sharing_consent": consent}}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=400, detail="No se pudo actualizar el consentimiento")


async def get_data_sharing_consent(company_id: str):
    """
    Obtiene el consentimiento de compartir datos de la empresa.
    """
    company = await db.companies.find_one({"_id": ObjectId(company_id)}, {"data_sharing_consent": 1, "_id": 0})

    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    return company 


async def get_delete_account_request(company_id: str):
    """
    Obtiene la solicitud de eliminación de cuenta de la empresa.
    """
    company = await db.companies.find_one({"_id": ObjectId(company_id)}, {"account_deletion_requested": 1, "_id": 0})

    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    return company 

async def get_gdpr_logs(company_id: str):
    """
    Obtiene los logs de acciones de GDPR (acceso o eliminación de datos) para la empresa.
    """
    company = await db.companies.find_one({"_id": ObjectId(company_id)}, {"gdpr_request_log": 1, "_id": 0})

    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    return company.get("gdpr_request_log", [])

class StripeService:
    @staticmethod
    def create_checkout_session(company_id: str) -> str:
        try:
            # Precio y producto según el plan
            price = 1999  # Precio en centavos (19,99 EUR)
            product_name = "Plan PRO"
            
            # Crear la sesión de Stripe
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": product_name,
                        },
                        "unit_amount": price,
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url="http://localhost:3000/confirm-plan",  # Redirige cuando el pago sea exitoso
                cancel_url="http://localhost:3000/subscriptions", # Redirige si se cancela el pago
                client_reference_id=company_id,  
            )
            return session.url
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error al crear la sesión de pago")

async def confirmar_pago(company_id: str):
    """Confirma el pago y actualiza el plan de la empresa a PRO con expiración en 1 mes."""
    expiration_date = datetime.utcnow() + timedelta(days=30)

    updated_company = await db.companies.find_one_and_update(
        {"_id": company_id},
        {"$set": {
            "subscription_plan": SubscriptionPlan.PRO,
            "subscription_expires_at": expiration_date
        }},
        return_document=ReturnDocument.AFTER
    )

    invoice_data = {
        "company_id": str(company_id),
        "plan": "PRO",
        "amount": 19.99,
        "issued_at": datetime.utcnow(),
        "status": "Pagado"
    }
    await db.invoices.insert_one(invoice_data)

    return {
        "status": "success",
        "message": "Plan actualizado correctamente",
        "expires_at": expiration_date
    }



async def check_expired_subscriptions():
    """Revisa qué empresas ya pasaron su fecha de expiración y las regresa al plan BÁSICO."""
    now = datetime.utcnow()

    result = await db.companies.update_many(
        {"subscription_plan": SubscriptionPlan.PRO, "subscription_expires_at": {"$lt": now}},
        {"$set": {"subscription_plan": SubscriptionPlan.BASICO}, "$unset": {"subscription_expires_at": ""}}
    )

    print(f"Planes degradados a BASICO: {result.modified_count}")