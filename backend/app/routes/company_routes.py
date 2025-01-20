from fastapi import APIRouter, HTTPException, Depends
from app.utils.security import hash_password, verify_password, create_access_token, get_current_user
from app.database import db
from app.schemas import CompanyCreate, CompanyResponse, Token, LoginRequest , UpdateCompanyProfile , UserResponse , UserCreate , UserUpdate , PasswordResetRequest, PasswordResetConfirm
from bson import ObjectId
from typing import List
from datetime import datetime
from app.services import send_email

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    email = login_data.email
    password = login_data.password

    # Buscar en empresas
    company = await db.companies.find_one({"email": email})
    if company and verify_password(password, company["password"]):
        token = create_access_token(data={
    "sub": company["email"],
    "role": "admin",
    "company_id": str(company["_id"])
})
        return {"access_token": token, "token_type": "bearer"}

    # Buscar en usuarios
    user = await db.users.find_one({"email": email})
    if user and verify_password(password, user["password"]):
        token = create_access_token(data={
    "sub": user["email"],
    "role": user["role"],
    "user_id": str(user["_id"])
})
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
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
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
            profileImage=company.profileImage,
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
        profileImage=company.get("profileImage"),
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
    updated_data["updated_at"] = datetime.utcnow()

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
        profileImage=updated_company.get("profileImage"),
        created_at=updated_company.get("created_at"),
        updated_at=updated_company.get("updated_at")
    )

@router.post("/reset-password")
async def reset_password(request: PasswordResetRequest):
    try:
        # Buscar el usuario en la base de datos
        user = await db.companies.find_one({"email": request.email})
        if not user:
            raise HTTPException(status_code=404, detail="Correo no registrado")

        # Crear un token de recuperación (ejemplo: simple hash)
        reset_token = "TOKEN_GENERADO_AQUI"

        # Guardar el token en la base de datos (opcional)
        await db.companies.update_one({"email": request.email}, {"$set": {"reset_token": reset_token}})

        # Crear enlace de recuperación
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"

        # Enviar el correo
        subject = "Recupera tu contraseña"
        content = f"""
        <h1>Recupera tu contraseña</h1>
        <p>Haz clic en el enlace para restablecer tu contraseña:</p>
        <a href="{reset_link}">{reset_link}</a>
        """
        send_email(request.email, subject, content)

        return {"message": "Correo de recuperación enviado"}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="No se pudo enviar el correo de recuperación")
    

@router.post("/reset-password-confirm")
async def reset_password_confirm(request: PasswordResetConfirm):
    try:
        # Verificar token
        user = await db.companies.find_one({"reset_token": request.token})
        if not user:
            raise HTTPException(status_code=400, detail="Token inválido o expirado")

        # Actualizar contraseña
        hashed_password = hash_password(request.password)
        await db.companies.update_one({"reset_token": request.token}, {
            "$set": {"password": hashed_password},
            "$unset": {"reset_token": ""},
        })

        return {"message": "Contraseña restablecida correctamente"}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error al restablecer contraseña")
    
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
            surname=user["surname"],
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

    hashed_password = hash_password(user.password)

    # Insertar el usuario en la base de datos
    user_data = user.dict()
    user_data["password"] = hashed_password
    user_data["company_id"] = ObjectId(company_id)

    result = await db.users.insert_one(user_data)

    return UserResponse(
        id=str(result.inserted_id),
        name=user.name,
        surname=user.surname,
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
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    company_id = ObjectId(current_user["company_id"])

    # Verificar si el usuario existe y pertenece a la empresa actual
    existing_user = await db.users.find_one({"_id": ObjectId(user_id), "company_id": company_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o no pertenece a tu empresa")

    # Actualizar datos del usuario, excluyendo el campo `password`
    updated_data = user_data.dict(exclude_unset=True)
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updated_data})

    # Retornar los datos actualizados
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
    return UserResponse(
        id=str(updated_user["_id"]),
        name=updated_user["name"],
        surname=updated_user.get("surname"),
        email=updated_user["email"],
        role=updated_user["role"]
    )



@router.get("/users/profile", response_model=UserResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Devuelve los datos del usuario logueado.
    """
    user = await db.users.find_one({"_id": ObjectId(current_user["user_id"])})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        surname=user["surname"],
        email=user["email"],
        role=user["role"],
    )
