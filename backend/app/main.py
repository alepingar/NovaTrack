from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from app.routes import company_routes  # Asegúrate de que este archivo esté correctamente configurado
from app.utils.security import create_access_token, verify_password
from app.database import db
from pydantic import BaseModel

# Configuración básica
SECRET_KEY = "secret_example_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# Rutas
app.include_router(company_routes.router, prefix="/companies", tags=["Companies"])

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Token para empresas
class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/token", response_model=Token)
async def login_for_access_token(email: str, password: str):
    # Buscar empresa en la base de datos
    company = await db.companies.find_one({"email": email})
    if not company or not verify_password(password, company["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Generar el token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": company["email"], "company_id": str(company["_id"]), "role": "admin"},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
