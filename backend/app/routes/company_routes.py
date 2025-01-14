from fastapi import APIRouter, HTTPException, Depends
from app.utils.security import hash_password, verify_password, create_access_token, get_current_user
from app.database import db
from app.schemas import CompanyCreate, CompanyResponse, Token, LoginRequest
from bson import ObjectId

router = APIRouter()

@router.post("/register", response_model=CompanyResponse)
async def register_company(company: CompanyCreate):
    # Verificar si la empresa ya existe
    existing_company = await db.companies.find_one({"email": company.email})
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
        role="admin"
    )

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    email = login_data.email
    password = login_data.password

    # Buscar en empresas
    company = await db.companies.find_one({"email": email})
    if company and verify_password(password, company["password"]):
        token = create_access_token(data={"sub": company["email"], "role": "admin", "company_id": str(company["_id"])})
        return {"access_token": token, "token_type": "bearer"}

    raise HTTPException(status_code=401, detail="Credenciales inválidas")

@router.get("/companies", response_model=list[CompanyResponse])
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

@router.get("/profile", response_model=CompanyResponse)
async def get_company_profile(current_user: dict = Depends(get_current_user)):
    # Buscar la empresa asociada al usuario logeado
    company = await db.companies.find_one({"_id": ObjectId(current_user["company_id"])})
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    return CompanyResponse(
        id=str(company["_id"]),
        name=company["name"],
        email=company["email"],
        industry=company.get("industry"),
        role="admin",
    )
