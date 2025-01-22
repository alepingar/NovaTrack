from app.database import db
from app.schemas import UserResponse, UserCreate, UserUpdate
from bson import ObjectId
from fastapi import HTTPException
from app.utils.security import hash_password
from typing import List

async def fetch_company_users(company_id: str) -> List[UserResponse]:
    """
    Obtiene todos los usuarios asociados a una empresa.
    """
    users = await db.users.find({"company_id": ObjectId(company_id)}).to_list(length=None)
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

async def create_company_user(company_id: str, user: UserCreate) -> UserResponse:
    """
    Crea un usuario asociado a una empresa.
    """
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya está registrado")

    hashed_password = hash_password(user.password)
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

async def delete_company_user(company_id: str, user_id: str):
    """
    Elimina un usuario asociado a una empresa.
    """
    user = await db.users.find_one({"_id": ObjectId(user_id), "company_id": ObjectId(company_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o no pertenece a tu empresa")
    await db.users.delete_one({"_id": ObjectId(user_id)})

async def update_company_user(company_id: str, user_id: str, user_data: UserUpdate) -> UserResponse:
    """
    Actualiza los datos de un usuario asociado a una empresa.
    """
    existing_user = await db.users.find_one({"_id": ObjectId(user_id), "company_id": ObjectId(company_id)})
    if not existing_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o no pertenece a tu empresa")

    updated_data = user_data.dict(exclude_unset=True)
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": updated_data})

    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
    return UserResponse(
        id=str(updated_user["_id"]),
        name=updated_user["name"],
        surname=updated_user.get("surname"),
        email=updated_user["email"],
        role=updated_user["role"]
    )

async def fetch_user_profile(user_id: str) -> UserResponse:
    """
    Obtiene el perfil de un usuario por su ID.
    """
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        surname=user["surname"],
        email=user["email"],
        role=user["role"],
    )
