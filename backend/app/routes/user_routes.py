from fastapi import APIRouter, HTTPException , status
from app.utils.security import hash_password , verify_password , create_access_token
from app.database import db
from app.schemas import CompanyCreate, CompanyResponse, Token, CompanyResponse, UserCreate, UserResponse , LoginRequest
from bson import ObjectId

router = APIRouter()

@router.post("/register/company", response_model=CompanyResponse)
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


@router.post("/register/user", response_model=UserResponse)
async def register_user(user: UserCreate):
    # Convertir company_id a ObjectId
    try:
        company_id = ObjectId(user.company_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de empresa inválido")

    # Verificar si la empresa existe
    company = await db.companies.find_one({"_id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    # Verificar si el usuario ya existe
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya está registrado")

    hashed_password = hash_password(user.password)
    user_data = user.dict()
    user_data["password"] = hashed_password
    user_data["company_id"] = company_id  # Guarda el ID como ObjectId
    result = await db.users.insert_one(user_data)
    return UserResponse(
        id=str(result.inserted_id),
        name=user.name,
        email=user.email,
        role=user.role,
        company_id=user.company_id,
    )

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    email = login_data.email
    password = login_data.password

    # Buscar en usuarios
    user = await db.users.find_one({"email": email})
    if user and verify_password(password, user["password"]):
        token = create_access_token(data={"sub": user["email"], "role": user["role"]})
        return {"access_token": token, "token_type": "bearer", "role": user["role"], "entity": "user"}

    # Buscar en empresas
    company = await db.companies.find_one({"email": email})
    if company and verify_password(password, company["password"]):
        token = create_access_token(data={"sub": company["email"], "role": "admin"})
        return {"access_token": token, "token_type": "bearer", "role": "admin", "entity": "company"}

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