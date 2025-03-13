from fastapi import APIRouter, Depends, HTTPException
from app.utils.security import get_current_user
from app.services.company_services import (
    fetch_companies,
    register_new_company,
    fetch_company_profile,
    upgrade_subscription,
    get_entity_types1,
    get_current_plan
)
from app.models.company import CompanyResponse, CompanyCreate, UpdateCompanyProfile, EntityType, SubscriptionPlan
from typing import List
from app.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[CompanyResponse])
async def get_companies():
    """
    Devuelve la lista de todas las empresas registradas.
    """
    return await fetch_companies()

@router.post("/register", response_model=CompanyResponse)
async def register_company(company: CompanyCreate):
    """
    Registra una nueva empresa.
    """
    return await register_new_company(company)

@router.get("/profile", response_model=CompanyResponse)
async def get_company_profile(current_user: dict = Depends(get_current_user)):
    """
    Devuelve el perfil de la empresa asociada al usuario autenticado.
    """
    return await fetch_company_profile(current_user["company_id"])


@router.put("/profile", response_model=CompanyResponse)
async def update_company_profile(
    company_data: UpdateCompanyProfile,
    current_user: dict = Depends(get_current_user)
):
    """
    Permite a una empresa actualizar su perfil.
    """
    print(company_data.dict())
    
    company_id = ObjectId(current_user["company_id"])
    existing_company = await db.companies.find_one({"_id": company_id})

    if not existing_company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    updated_data = company_data.dict(exclude_unset=True)
    updated_data["updated_at"] = datetime.utcnow().isoformat()

    await db.companies.update_one({"_id": company_id}, {"$set": updated_data})

    updated_company = await db.companies.find_one({"_id": company_id})
    return CompanyResponse(
        id=str(updated_company["_id"]),
        name=updated_company["name"],
        email=updated_company["email"],
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


@router.get("/get-types", response_model=List[EntityType])
async def get_entity_types():
    """
    Devuelve la lista de tipos de entidad legal.
    """
    return await get_entity_types1()


@router.put("/upgrade-plan/{new_plan}", response_model=CompanyResponse)
async def upgrade_plan(new_plan: str, current_user: dict = Depends(get_current_user)):
    """
    Actualiza el plan de suscripción de la empresa y genera una factura.
    """
    print(f"🔍 Recibido en el backend: {new_plan}")
    try:
        new_plan_enum = SubscriptionPlan(new_plan.upper())  
    except ValueError:
        print("❌ Error: Plan de suscripción inválido")
        raise HTTPException(status_code=422, detail="Plan de suscripción inválido")

    return await upgrade_subscription(current_user["company_id"], new_plan_enum)


@router.get("/get-current-plan", response_model=str)
async def get_plan(current_user: dict = Depends(get_current_user)):
    """
    Devuelve el plan de suscripción actual de la empresa.
    """
    return await get_current_plan(current_user["company_id"])


