from fastapi import APIRouter, File, UploadFile, HTTPException
import shutil
import os

router = APIRouter()

UPLOAD_DIR = "./uploads"

# Crear el directorio de uploads si no existe
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/logo")
async def upload_logo(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos de imagen.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"file_url": f"/uploads/{file.filename}"}
