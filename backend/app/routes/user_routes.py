from fastapi import APIRouter, HTTPException , status
from app.utils.security import hash_password , verify_password , create_access_token
from app.database import db
from app.schemas import CompanyCreate, CompanyResponse, CompanyLogin, Token

router = APIRouter()

@router.post("/register", response_model=CompanyResponse)
async def register_company(company: CompanyCreate):
    # Verificar si la empresa ya existe
    existing_company = await db.companies.find_one({"email": company.email})
    print(f"Resultado de find_one: {existing_company}")
    if existing_company:
        raise HTTPException(status_code=400, detail="La empresa ya está registrada")

    # Hashear la contraseña
    hashed_password = hash_password(company.password)
    company.password = hashed_password

    # Insertar en la base de datos
    result = await db.companies.insert_one(company.dict())
    return CompanyResponse(
        id=str(result.inserted_id),
        name=company.name,
        email=company.email,
        industry=company.industry,
        role = "admin"
    )


@router.post("/login", response_model=Token)
async def login_company(company: CompanyLogin):

    company_in_db = await db.companies.find_one({"email": company.email})
    if not company_in_db:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    if not verify_password(company.password, company_in_db["password"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    access_token = create_access_token(data={"sub": company_in_db["email"]})
    return {"access_token": access_token, "token_type": "bearer"}