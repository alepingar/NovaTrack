from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId
from app.utils.security import hash_password, verify_password, create_access_token
from app.database import db
from app.schemas import Token, LoginRequest, PasswordResetRequest, PasswordResetConfirm
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