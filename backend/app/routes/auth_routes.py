# auth_routes.py
from fastapi import APIRouter, HTTPException
from app.models.auth import EmailCheckResponse, Token, LoginRequest, PasswordResetRequest, PasswordResetConfirm
from app.services.auth_services import authenticate_user, generate_reset_token, reset_user_password, check_email

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """
    Authenticate a user and return a JWT token.
    """
    try:
        token = await authenticate_user(login_data.email, login_data.password)
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException as e:
        raise e


@router.post("/reset-password")
async def reset_password(request: PasswordResetRequest):
    """
    Generate a password reset token and send email.
    """
    try:
        return await generate_reset_token(request.email)
    except HTTPException as e:
        raise e


@router.post("/reset-password-confirm")
async def reset_password_confirm(request: PasswordResetConfirm):
    """
    Confirm password reset using token and new password.
    """
    try:
        return await reset_user_password(request.token, request.password)
    except HTTPException as e:
        raise e


@router.get("/check-email/{email}", response_model=EmailCheckResponse)
async def check_email_route(email: str):
    """
    Check if the email exists in the database.
    """
    exists = await check_email(email)
    return EmailCheckResponse(exists=exists)