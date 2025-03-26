from pydantic import BaseModel, EmailStr, Field
from pydantic_settings import BaseSettings


# Login Schema
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=50, description="La contraseña debe tener entre 8 y 50 caracteres")


class EmailCheckResponse(BaseModel):
    exists: bool

# Password Reset Schemas
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    password: str = Field(..., min_length=8, max_length=50, description="La nueva contraseña debe tener entre 8 y 50 caracteres")

# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str

class Settings(BaseSettings):
     email_host: str
     email_port: int
     email_user: str
     email_password: str
     email_from: str
     email_name: str
 
     class Config:
         env_file = ".env"
         extra = "allow"
 
settings = Settings()