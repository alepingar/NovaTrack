@echo off

:: Cambia al directorio de MongoDB y ejecuta el servidor
start cmd /k "mongod --dbpath C:\data\db"

:: Vuelve al directorio de NovaTrack y activa el entorno virtual
cd /d C:\Users\alexander\Desktop\NovaTrack
start cmd /k "venv\Scripts\activate && cd backend && uvicorn app.main:app --reload"

:: Inicia el frontend
cd /d C:\Users\alexander\Desktop\NovaTrack
start cmd /k "cd frontend && npm start"
