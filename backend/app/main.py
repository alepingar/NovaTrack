from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import company_routes, transfer_routes , upload_routes
from app.database import db
from fastapi.staticfiles import StaticFiles

import os

UPLOAD_DIR = "./uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


app = FastAPI()

# Rutas

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(company_routes.router, prefix="/companies", tags=["Companies"])
app.include_router(transfer_routes.router, prefix="/companies", tags=["Transfers"])
app.include_router(upload_routes.router, prefix="/upload", tags=["Uploads"])

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)