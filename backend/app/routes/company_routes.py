from fastapi import APIRouter, HTTPException, Depends
from app.utils.security import hash_password, verify_password, create_access_token, get_current_user
from app.database import db
from app.schemas import CompanyCreate, CompanyResponse, Token, LoginRequest , UpdateCompanyProfile , UserResponse , UserCreate
from bson import ObjectId
from typing import List

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


@router.put("/profile", response_model=CompanyResponse)
async def update_company_profile(
    company_data: UpdateCompanyProfile,
    current_user: dict = Depends(get_current_user)
):
    """
    Permite a una empresa actualizar su perfil.
    """
    company_id = ObjectId(current_user["company_id"])
    existing_company = await db.companies.find_one({"_id": company_id})

    if not existing_company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    # Actualizar datos
    updated_data = {
        "name": company_data.name,
        "email": company_data.email,
        "industry": company_data.industry
    }
    await db.companies.update_one({"_id": company_id}, {"$set": updated_data})

    # Retornar los datos actualizados
    updated_company = await db.companies.find_one({"_id": company_id})
    return CompanyResponse(
        id=str(updated_company["_id"]),
        name=updated_company["name"],
        email=updated_company["email"],
        industry=updated_company.get("industry"),
        role="admin"
    )


@router.get("/users", response_model=List[UserResponse])
async def get_company_users(current_user: dict = Depends(get_current_user)):
    """
    Devuelve la lista de usuarios asociados a la empresa actual.
    """
    company_id = ObjectId(current_user["company_id"])
    users = await db.users.find({"company_id": company_id}).to_list(length=None)
    return [
        UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            role=user["role"],
        )
        for user in users
    ]


@router.post("/users", response_model=UserResponse)
async def create_user(
    user: UserCreate, 
    current_user: dict = Depends(get_current_user)
):
    """
    Crear un nuevo usuario asociado a una empresa.
    """
    # Obtener el ID de la empresa del usuario actual
    company_id = current_user["company_id"]

    # Verificar si el usuario ya existe
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya está registrado")

    # Insertar el usuario en la base de datos
    user_data = user.dict()
    user_data["company_id"] = ObjectId(company_id)
    result = await db.users.insert_one(user_data)

    return UserResponse(
        id=str(result.inserted_id),
        name=user.name,
        email=user.email,
        role=user.role,
        company_id=company_id
    )


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Eliminar un usuario asociado a la empresa actual.
    """
    company_id = ObjectId(current_user["company_id"])

    # Verificar que el usuario pertenece a la empresa actual
    user = await db.users.find_one({"_id": ObjectId(user_id), "company_id": company_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o no pertenece a tu empresa")

    # Eliminar el usuario
    await db.users.delete_one({"_id": ObjectId(user_id)})
    return {"message": "Usuario eliminado correctamente"}



@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Editar los datos de un usuario asociado a la empresa actual.
    """
    company_id = ObjectId(current_user["company_id"])

    # Verificar que el usuario pertenece a la empresa actual
    existing_user = await db.users.find_one({"_id": ObjectId(user_id), "company_id": company_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o no pertenece a tu empresa")

    # Actualizar datos del usuario
    updated_data = user_data.dict()
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updated_data})

    # Retornar los datos actualizados
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
    return UserResponse(
        id=str(updated_user["_id"]),
        name=updated_user["name"],
        email=updated_user["email"],
        role=updated_user["role"],
        company_id=str(updated_user["company_id"])
    )