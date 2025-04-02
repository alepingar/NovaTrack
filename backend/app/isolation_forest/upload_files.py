from bson import Binary
import uuid
from app.models.transfer import Transfer
from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter
import xml.etree.ElementTree as ET
import pandas as pd
import joblib
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from app.services.notification_services import save_notification
from app.database import db
from dateutil import parser
import logging
from bson import ObjectId

# Cargar el modelo Isolation Forest
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "isolation_forest.pkl")
model = joblib.load(MODEL_PATH)

transfers_collection = db["transfers"]

# Mapeo de estados de transferencias
status_mapping = {"pendiente": 0, "completada": 1, "fallida": 2}

status_mapping1 = {
    "BOOK": "completada",
    "PEND": "pendiente",
    "REJ": "fallida",  # Añadir más códigos según sea necesario
}

async def fetch_company_stats():
    """Obtiene la media y desviación estándar de los montos por cada empresa."""
    cursor = transfers_collection.find({})
    data = await cursor.to_list(length=None)

    df = pd.DataFrame(data)

    # Si el DataFrame está vacío, devolver un diccionario vacío
    return {} if df.empty else df.groupby("company_id")["amount"].agg(["mean", "std"]).fillna(0).to_dict(orient="index")

async def process_transfer(transfer, company_stats):
    """Procesa una transferencia y la analiza con Isolation Forest."""
    try:
        company_id = transfer.get("company_id")
        amount = transfer.get("amount", 0)
        timestamp = parser.isoparse(str(transfer["timestamp"]))  # Convertir a string antes de parsear

        # Convertir el UUID a cadena inmediatamente después de obtenerlo
        transfer_id = transfer.get("id")
        if isinstance(transfer_id, bytes):
            transfer_id = str(uuid.UUID(bytes=transfer_id))
        elif isinstance(transfer_id, uuid.UUID):
            transfer_id = str(transfer_id)
        else:
            transfer_id = str(transfer_id)

        # Obtener estadísticas de la empresa
        stats = company_stats.get(company_id, {"mean": 0, "std": 1})
        amount_mean, amount_std = stats["mean"], stats["std"] or 1  # Evitar división por 0

        # Calcular Z-score
        amount_zscore = (amount - amount_mean) / amount_std
        status_numeric = status_mapping.get(transfer["status"], -1)
        
        is_banking_hour = transfer["timestamp"].hour
        is_banking_hour = 1 if (8 <= is_banking_hour < 22) else 0
        # Preparar datos para el modelo
        data = pd.DataFrame([[is_banking_hour, amount_zscore, status_numeric]],
                            columns=["is_banking_hour", "amount_zscore", "status"])

        # Predecir anomalía
        is_anomalous = bool(model.predict(data)[0] == -1)  # Convertir a bool de Python
        transfer["is_anomalous"] = is_anomalous
        transfer["timestamp"] = timestamp
        transfer["id"] = str(uuid.uuid4()) if "id" not in transfer else transfer["id"]
        # Guardar en MongoDB
        inserted = await transfers_collection.insert_one(transfer)
        transfer["_id"] = inserted.inserted_id

        if is_anomalous:
            message = f"⚠️ Alerta: Se detectó una transferencia anómala con ID: {transfer_id}"
            await save_notification(message, "Anomalía", company_id=transfer["company_id"])

        transfer["id"] = transfer_id
        return transfer
    except Exception as e:
        # Usar el transfer_id que ya es una cadena
        raise HTTPException(status_code=400, detail=f"Error procesando transferencia: {e}")

async def get_to_account(company_id: str):
    """Obtiene la cuenta de facturación de la empresa."""
    try:
        company_id_object = ObjectId(company_id)
        company = await db.companies.find_one({"_id": company_id_object}, {"billing_account_number": 1})
        if company:
            return company.get("billing_account_number")
        else:
            raise HTTPException(status_code=404, detail="Empresa no encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la cuenta de la empresa: {e}")

async def upload_camt_file(file: UploadFile, company_id: str):
    """Recibe un archivo CAMT.053.xml, extrae las transferencias y las analiza."""
    try:
        contents = await file.read()

        tree = ET.ElementTree(ET.fromstring(contents))  # Parsear el XML
        root = tree.getroot()

        # Namespace para el XML
        ns = {'camt': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.08'}
        entries = root.findall(".//camt:Bal", ns)  # Buscamos los elementos de tipo 'Bal'

        # Procesar cada entrada
        transfers = []
        for entry in entries:
            # Asegúrate de que los elementos existan antes de acceder a sus valores
            amount_element = entry.find(".//camt:Amt", ns)
            amount = float(amount_element.text) if amount_element is not None else 0.50
            if amount <= 0:
                amount = 1.0
            currency_element = entry.find(".//camt:Amt", ns)
            currency = currency_element.attrib["Ccy"] if currency_element is not None else "EUR"
            from_account_element = entry.find(".//camt:Acct/camt:Id/camt:IBAN", ns)
            from_account = from_account_element.text if from_account_element is not None else "Desconocido"
            to_account_element = entry.find(".//camt:Acct/camt:Id/camt:IBAN", ns)
            to_account = to_account_element.text if to_account_element is not None else await get_to_account(company_id)
            status_element = entry.find(".//camt:Sts/camt:Cd", ns)
            status_code = status_element.text if status_element is not None else "PEND"
            status = status_mapping1.get(status_code, "pendiente")
            timestamp_element = entry.find(".//camt:Dt/camt:DtTm", ns)
            timestamp = datetime.strptime(timestamp_element.text, "%Y-%m-%dT%H:%M:%S.%fZ") if timestamp_element is not None else datetime.now()
            transfer = Transfer(
                id=str(uuid.uuid4()),  # Generamos un ID único
                amount=amount,
                currency=currency,
                from_account=from_account,
                to_account=to_account,
                timestamp=timestamp,
                status=status,
                company_id=company_id,  # Esto debe ser dinámico
                is_anomalous=False,  # Definir si es anómalo
            ).model_dump() # Convertir a diccionario
            transfers.append(transfer)

        company_stats = await fetch_company_stats()
        for transfer in transfers:
            transfer["id"] = str(uuid.uuid4())
        
        
        tasks = [process_transfer(tx, company_stats) for tx in transfers]
        results = await asyncio.gather(*tasks)

        # Convertir ObjectId a string antes de devolver la respuesta
        for result in results:
            if "_id" in result:
                result["_id"] = str(result["_id"])
        return {"message": "Archivo procesado correctamente", "processed_transfers": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {e}")