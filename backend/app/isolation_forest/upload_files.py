import random
import numpy as np
import uuid
from app.models.transfer import Transfer
from fastapi import UploadFile, HTTPException
import xml.etree.ElementTree as ET
import pandas as pd
import joblib
import os
from datetime import datetime, timezone
from app.services.notification_services import save_notification
from app.database import db
from dateutil import parser
from bson import ObjectId

# Cargar el modelo Isolation Forest
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "isolation_forest.pkl")
model = joblib.load(MODEL_PATH)

transfers_collection = db["transfers"]

# Mapeo de estados de transferencias (para el modelo)
status_mapping = {"pendiente": 0, "completada": 1, "fallida": 2}
status_columns = ['status_completada', 'status_fallida', 'status_pendiente']

# Mapeo de estados de transferencias desde el XML
status_mapping_xml = {
    "BOOK": "completada",
    "PEND": "pendiente",
    "REJ": "fallida",  # Añadir más códigos según sea necesario
}

async def fetch_company_stats():
    """Obtiene la media, desviación estándar, Q5 y Q95 de los montos por cada empresa."""
    cursor = transfers_collection.find({})
    data = await cursor.to_list(length=None)
    df = pd.DataFrame(data)
    if df.empty:
        return {}
    return df.groupby("company_id")["amount"].agg(["mean", "std", lambda x: x.quantile(0.05), lambda x: x.quantile(0.95)]).rename(columns={'<lambda_0>': 'q5', '<lambda_1>': 'q95'}).fillna(0).to_dict(orient="index")

async def get_recurrent_clients():
    """Obtiene un conjunto de 'from_account' que han aparecido más de una vez."""
    pipeline = [
        {"$group": {"_id": "$from_account", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
        {"$project": {"_id": 1}}
    ]
    recurrent_accounts_data = await transfers_collection.aggregate(pipeline).to_list(length=None)
    return {item['_id'] for item in recurrent_accounts_data}

async def process_transfer(transfer, company_stats, recurrent_clients):
    """Procesa una transferencia y la analiza con Isolation Forest."""
    try:
        company_id = transfer.get("company_id")
        amount = transfer.get("amount", 0)
        timestamp = parser.isoparse(str(transfer["timestamp"]))

        transfer_id = transfer.get("id")
        if isinstance(transfer_id, bytes):
            transfer_id = str(uuid.UUID(bytes=transfer_id))
        elif isinstance(transfer_id, uuid.UUID):
            transfer_id = str(transfer_id)
        else:
            transfer_id = str(transfer_id)

        # Obtener el número de transferencias existentes para la compañía
        existing_transfers_count = await transfers_collection.count_documents({"company_id": company_id})

        # Si hay menos de 30 transferencias, marcar como no anómala y guardar
        if existing_transfers_count < 30:
            transfer["is_anomalous"] = False
            transfer["timestamp"] = timestamp
            transfer["id"] = str(uuid.uuid4()) if "id" not in transfer else transfer["id"]
            inserted = await transfers_collection.insert_one(transfer)
            transfer["_id"] = inserted.inserted_id
            transfer["id"] = transfer_id # Restaurar el ID original para la respuesta
            return transfer

        # Obtener estadísticas de la empresa
        stats = company_stats.get(company_id, {"mean": 0, "std": 1, "q5": 0, "q95": 0})
        amount_mean = stats["mean"]
        amount_std = stats["std"] or 1
        amount_iqr_low = stats["q5"]
        amount_iqr_high = stats["q95"]

        # Calcular Z-score
        amount_zscore = (amount - amount_mean) / amount_std

        # Calcular si está fuera del IQR
        is_outside_iqr = 1 if (amount < amount_iqr_low or amount > amount_iqr_high) else 0

        # Determinar si el cliente es recurrente
        is_recurrent_client = 1 if transfer.get("from_account") in recurrent_clients else 0

        # Crear características One-Hot para 'status'
        status_one_hot = pd.Series([0] * len(status_columns), index=status_columns)
        status = transfer.get("status")
        if status in status_mapping:
            status_index = list(status_mapping.keys()).index(status)
            if 0 <= status_index < len(status_columns):
                status_one_hot[status_columns[status_index]] = 1

        # Crear DataFrame con las características para el modelo
        features = {
            "amount_zscore": [amount_zscore],
            "is_recurrent_client": [is_recurrent_client],
            "hour": [timestamp.hour],
            "is_outside_iqr": [is_outside_iqr],
        }
        features.update(status_one_hot.to_dict())
        data = pd.DataFrame(features)

        # Asegurarse de que el orden de las columnas coincida con el modelo entrenado
        expected_columns = ["amount_zscore", "is_recurrent_client", "hour", "is_outside_iqr"] + status_columns
        data = data.reindex(columns=expected_columns, fill_value=0)

        # Predecir anomalía
        anomaly_score = model.score_samples(data)[0]
        threshold = np.percentile(model.score_samples(pd.DataFrame(np.zeros((1, len(expected_columns))), columns=expected_columns)), 7.5) # Usar el mismo umbral
        is_anomalous = bool(anomaly_score < threshold)

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
        raise HTTPException(status_code=400, detail=f"Error procesando transferencia: {e}")

BANCOS_ESP = [
    "0049",  # Santander
    "0075",  # Banco Popular
    "0081",  # Banco Sabadell
    "2100",  # CaixaBank
    "0182",  # BBVA
    "1465",  # ING
    "0128",  # Bankinter
    "2038",  # Bankia (fusionado con CaixaBank)
]

async def generate_iban_es():
    country_code = "ES"
    check_digits = f"{random.randint(10, 99)}"  # Dos dígitos de control
    bank_code = random.choice(BANCOS_ESP)  # Selecciona un banco real
    branch_code = f"{random.randint(1000, 9999)}"  # Código de sucursal (4 dígitos)
    account_number = f"{random.randint(100000000000, 999999999999)}"  # 12 dígitos

    return f"{country_code}{check_digits}{bank_code}{branch_code}{account_number}"

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

async def increment_uploads_count(company_id: str):
    """Incrementa el contador de subidas de archivos de la empresa."""
    await db.companies.update_one({"_id": ObjectId(company_id)}, {"$inc": {"uploads_count": 1}})

async def upload_camt_file(file: UploadFile, company_id: str):
    from xml.etree.ElementTree import ElementTree
    try:
        company = await db.companies.find_one({"_id": ObjectId(company_id)})
        if not company:
            raise HTTPException(status_code=404, detail="Empresa no encontrada.")

        current_plan = company.get("subscription_plan", "BASICO")
        uploads_count = company.get("uploads_count", 0)

        if current_plan == "BASICO" and uploads_count >= 20:
            raise HTTPException(status_code=403, detail="Has alcanzado el límite de tu plan.")

        contents = await file.read()
        tree = ET.ElementTree(ET.fromstring(contents))
        ns = {"camt": "urn:iso:std:iso:20022:tech:xsd:camt.053.001.08"}

        transfers = []

        for stmt in tree.findall(".//camt:Stmt", ns):
            to_account_element = stmt.find("camt:Acct/camt:Id/camt:IBAN", ns)
            to_account = to_account_element.text if to_account_element is not None else await get_to_account(company_id)

            for entry in stmt.findall("camt:Ntry", ns):
                amount_elem = entry.find("camt:Amt", ns)
                amount = float(amount_elem.text) if amount_elem is not None else 0.50
                currency = amount_elem.attrib.get("Ccy", "EUR") if amount_elem is not None else "EUR"

                status_elem = entry.find("camt:Sts/camt:Cd", ns)
                status_code = status_elem.text if status_elem is not None else None
                status = status_mapping_xml.get(status_code, random.choices(["completada", "pendiente", "fallida"], weights=[94, 3, 3])[0])

                credit_debit = entry.find("camt:CdtDbtInd", ns)
                cd_indicator = credit_debit.text if credit_debit is not None else "CRDT"

                book_date = entry.find("camt:BookgDt/camt:DtTm", ns)
                timestamp_str = book_date.text if book_date is not None else datetime.now().isoformat()

                try:
                    timestamp = parser.isoparse(timestamp_str)
                except Exception:
                    timestamp = datetime.now(timezone.utc)

                for tx_detail in entry.findall(".//camt:NtryDtls/camt:TxDtls", ns):
                    refs = tx_detail.find("camt:Refs", ns)
                    tx_id = refs.find("camt:TxId", ns).text if refs is not None and refs.find("camt:TxId", ns) is not None else str(uuid.uuid4())

                    debtor_iban_elem = tx_detail.find(".//camt:DbtrAcct/camt:Id/camt:IBAN", ns)
                    creditor_iban_elem = tx_detail.find(".//camt:CdtrAcct/camt:Id/camt:IBAN", ns)

                    if cd_indicator == "CRDT":
                        from_account = debtor_iban_elem.text if debtor_iban_elem is not None else await generate_iban_es()
                    else:
                        from_account = creditor_iban_elem.text if creditor_iban_elem is not None else await generate_iban_es()

                    transfer_data = Transfer(
                        id=str(uuid.uuid4()),
                        amount=amount,
                        currency=currency,
                        from_account=from_account,
                        to_account=to_account,
                        timestamp=timestamp,
                        status=status,
                        company_id=company_id,
                        is_anomalous=False, # Inicialmente marcamos todas como no anómalas
                    ).model_dump()

                    transfers.append(transfer_data)

        if not transfers:
            raise HTTPException(status_code=400, detail="No se encontraron transferencias válidas en el archivo.")

        company_stats = await fetch_company_stats()
        recurrent_clients = await get_recurrent_clients()
        processed_transfers = []
        for transfer in transfers:
            transfer["id"] = str(uuid.uuid4())
            processed_transfer = await process_transfer(transfer, company_stats, recurrent_clients)
            processed_transfers.append(processed_transfer)

        await increment_uploads_count(company_id)

        for result in processed_transfers:
            if "_id" in result:
                result["_id"] = str(result["_id"])
        return {"message": "Archivo procesado correctamente", "processed_transfers": processed_transfers}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {e}")