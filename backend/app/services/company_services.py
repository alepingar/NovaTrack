from app.database import db
from app.models.company import CompanyResponse, CompanyCreate, UpdateCompanyProfile, EntityType, SubscriptionPlan
from bson import ObjectId
from fastapi import HTTPException
from app.utils.security import hash_password
from datetime import datetime
from typing import List

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
        )
        for company in companies
    ]

async def register_new_company(company: CompanyCreate) -> CompanyResponse:
    """
    Registra una nueva empresa.
    """
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
    })

    result = await db.companies.insert_one(company_data)

    return CompanyResponse(
        id=str(result.inserted_id),
        name=company.name,
        email=company.email,
        industry=company.industry,
        role=company.role,
        country=company.country,
        phone_number=company.phone_number,
        tax_id=company.tax_id,
        website=company.website,
        description=company.description,
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
        role=company.get("role"),
        country=company.get("country"),
        phone_number=company.get("phone_number"),
        tax_id=company.get("tax_id"),
        website=company.get("website"),
        description=company.get("description"),
        address=company.get("address"),
        founded_date=company.get("founded_date"),
        created_at=company.get("created_at"),
        updated_at=company.get("updated_at"),
        billing_account_number=company.get("billing_account_number")
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
        role=updated_company.get("role"),
        country=updated_company.get("country"),
        phone_number=updated_company.get("phone_number"),
        tax_id=updated_company.get("tax_id"),
        website=updated_company.get("website"),
        description=updated_company.get("description"),
        address=updated_company.get("address"),
        founded_date=updated_company.get("founded_date"),
        created_at=updated_company.get("created_at"),
        updated_at=updated_company.get("updated_at")
    )


async def get_entity_types1() -> List[EntityType]:
    return [entity for entity in EntityType]


async def upgrade_subscription(company_id: str, new_plan: SubscriptionPlan) -> CompanyResponse:
    """
    Actualiza el plan de suscripción de una empresa y genera una factura.
    """
    company = await db.companies.find_one({"_id": ObjectId(company_id)})
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    current_plan = company.get("subscription_plan")

    # Si el plan actual es igual al nuevo plan, no se hace nada
    if current_plan == new_plan:
        raise HTTPException(status_code=400, detail="Ya estás en este plan")

    # Lógica de precios de planes
    plan_prices = {
        SubscriptionPlan.BASICO: 0,
        SubscriptionPlan.NORMAL: 19.99,
        SubscriptionPlan.PRO: 39.99,
    }

    # Si el usuario está en un plan superior al nuevo plan, no le dejamos hacer el downgrade
    if (
        (current_plan == SubscriptionPlan.NORMAL and new_plan == SubscriptionPlan.BASICO) or
        (current_plan == SubscriptionPlan.PRO and new_plan in [SubscriptionPlan.BASICO, SubscriptionPlan.NORMAL])
    ):
        raise HTTPException(status_code=400, detail="No puedes bajar a un plan inferior una vez hayas pagado por uno superior")

    # Si el nuevo plan es diferente y no es un downgrade, generamos la factura si es necesario
    if new_plan != SubscriptionPlan.BASICO:  # Solo genera factura si el plan es diferente a Básico
        invoice_data = {
            "company_id": company_id,
            "plan": new_plan.value,
            "amount": plan_prices[new_plan],
            "issued_at": datetime.utcnow(),
            "status": "Pagado"
        }
        await db.invoices.insert_one(invoice_data)

    # Actualizar el plan de suscripción
    await db.companies.update_one(
        {"_id": ObjectId(company_id)},
        {"$set": {"subscription_plan": new_plan.value, "updated_at": datetime.utcnow().isoformat()}}
    )

    updated_company = await db.companies.find_one({"_id": ObjectId(company_id)})
    return CompanyResponse(
        id=str(updated_company["_id"]),
        name=updated_company.get("name"),
        email=updated_company.get("email"),
        industry=updated_company.get("industry"),
        role=updated_company.get("role"),
        country=updated_company.get("country"),
        phone_number=updated_company.get("phone_number"),
        tax_id=updated_company.get("tax_id"),
        website=updated_company.get("website"),
        description=updated_company.get("description"),
        address=updated_company.get("address"),
        founded_date=updated_company.get("founded_date"),
        created_at=updated_company.get("created_at"),
        updated_at=updated_company.get("updated_at"),
        subscription_plan=updated_company.get("subscription_plan")
    )

async def get_current_plan(company_id: str) -> str:
    company = await db.companies.find_one({"_id": ObjectId(company_id)})
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    return company.get("subscription_plan", 0)