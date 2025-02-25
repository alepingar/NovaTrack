from app.database import db
from app.models.company import CompanyResponse, CompanyCreate, UpdateCompanyProfile, EntityType
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
        updated_at=company.get("updated_at")
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