from fastapi import APIRouter, Depends
from app.utils.security import get_current_user
from app.services.user_services import (
    fetch_company_users,
    create_company_user,
    delete_company_user,
    update_company_user,
    fetch_user_profile
)
from app.schemas import UserResponse, UserCreate, UserUpdate
from typing import List

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_company_users(current_user: dict = Depends(get_current_user)):
    """
    Devuelve la lista de usuarios asociados a la empresa actual.
    """
    company_id = current_user["company_id"]
    return await fetch_company_users(company_id)

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, current_user: dict = Depends(get_current_user)):
    """
    Crea un nuevo usuario asociado a una empresa.
    """
    company_id = current_user["company_id"]
    return await create_company_user(company_id, user)

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """
    Elimina un usuario asociado a la empresa actual.
    """
    company_id = current_user["company_id"]
    await delete_company_user(company_id, user_id)
    return {"message": "Usuario eliminado correctamente"}

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_data: UserUpdate, current_user: dict = Depends(get_current_user)):
    """
    Actualiza los datos de un usuario.
    """
    company_id = current_user["company_id"]
    return await update_company_user(company_id, user_id, user_data)

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Devuelve el perfil del usuario logueado.
    """
    user_id = current_user["user_id"]
    return await fetch_user_profile(user_id)
