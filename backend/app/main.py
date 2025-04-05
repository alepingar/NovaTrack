from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import company_routes, transfer_routes , auth_routes , notification_routes , invoice_routes
import os
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
app = FastAPI()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Manejo de la conexión con MongoDB
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongodb_client = AsyncIOMotorClient(MONGO_URI)
    app.db = app.mongodb_client["nova_track"]
    yield
    app.mongodb_client.close()

# Instancia de FastAPI
app = FastAPI(lifespan=lifespan)
    
# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000",os.getenv("FRONTEND_URL", "https://tu-dominio.com")],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(company_routes.router, prefix="/companies", tags=["Companies"])
app.include_router(transfer_routes.router, prefix="/transfers", tags=["Transfers"])
app.include_router(notification_routes.router, prefix="/notifications",tags=["Notifications"])
app.include_router(invoice_routes.router, prefix="/invoices",tags=["Invoices"])