from fastapi import APIRouter, HTTPException, Depends
from app.utils.security import hash_password, verify_password, create_access_token, get_current_user
from app.database import db
from app.schemas import CompanyCreate, CompanyResponse, Token, LoginRequest , UpdateCompanyProfile , UserResponse , UserCreate , UserUpdate , PasswordResetRequest, PasswordResetConfirm
from bson import ObjectId
from typing import List
from datetime import datetime
from app.services import send_email

router = APIRouter()



@router.get("/", response_model=list[CompanyResponse])
async def get_companies():
    """
    Devuelve la lista de todas las empresas registradas.
    """
    companies = await db.companies.find().to_list(length=None)
    return [
        CompanyResponse(
            id=str(company["_id"]),
            name=company["name"],
            email=company["email"],
            industry=company.get("industry", None),
        )
        for company in companies
    ]

@router.post("/register", response_model=CompanyResponse)
async def register_company(company: CompanyCreate):
    try:
        print(f"Datos recibidos: {company.dict()}")
        # Verificar si la empresa ya existe

        if company.password != company.confirm_password:
            raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")
        
        existing_company = await db.companies.find_one({"email": company.email})
        if existing_company:
            raise HTTPException(status_code=400, detail="La empresa ya está registrada")

        # Hashear la contraseña
        hashed_password = hash_password(company.password)
        

        # Agregar campos adicionales
        company_data = company.dict()
        company_data.pop("confirm_password")
        company_data.update({
            "password": hashed_password,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        })

        # Insertar en la base de datos
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
            updated_at=company_data["updated_at"]
        )
    except Exception as e:
        print(f"Error: {e}")
        raise


@router.get("/profile", response_model=CompanyResponse)
async def get_company_profile(current_user: dict = Depends(get_current_user)):
    # Buscar la empresa asociada al usuario logeado
    company = await db.companies.find_one({"_id": ObjectId(current_user["company_id"])});
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

    # Actualizar datos
    updated_data = company_data.dict(exclude_unset=True)
    updated_data["updated_at"] = datetime.utcnow().isoformat()

    await db.companies.update_one({"_id": company_id}, {"$set": updated_data})

    # Retornar los datos actualizados
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


    
