from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from app.routes import company_routes, transfer_routes
from app.utils.security import create_access_token, verify_password
from app.database import db
from pydantic import BaseModel


app = FastAPI()

# Rutas
app.include_router(company_routes.router, prefix="/companies", tags=["Companies"])
app.include_router(transfer_routes.router, prefix="/companies", tags=["Transfers"])
# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)