from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from app.utils.security import get_current_user, hash_password
from app.database import db
from typing import List
from app.schemas import UserResponse, UserCreate, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
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


@router.post("/", response_model=UserResponse)
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


@router.delete("/{user_id}", status_code=204)
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



@router.put("/{user_id}", response_model=UserResponse)
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



@router.get("/profile", response_model=UserResponse)
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
