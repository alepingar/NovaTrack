from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import company_routes, transfer_routes, user_routes , auth_routes

app = FastAPI()

# Rutas

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(user_routes.router, prefix="/users", tags=["Users"])
app.include_router(company_routes.router, prefix="/companies", tags=["Companies"])
app.include_router(transfer_routes.router, prefix="/transfers", tags=["Transfers"])

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)