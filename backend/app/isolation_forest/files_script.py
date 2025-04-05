import os
import xml.etree.ElementTree as ET
from datetime import datetime
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from bson import Binary
import uuid

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = AsyncIOMotorClient(MONGO_URI)
db = client["nova_track"]

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configura la carpeta donde se guardan los archivos CAMT.053
CAMT_FOLDER = "./camt_files/"  # Cambia a la ruta de la carpeta donde subes los archivos

class Transfer(BaseModel):
    id: UUID  # ID único de la transferencia (camt.053)
    amount: float = Field(..., gt=0, description="Monto de la transacción (camt.053)")
    currency: str = Field(..., min_length=3, max_length=3, description="Moneda de la transacción (camt.053)")
    from_account: str = Field(..., min_length=10, max_length=24, description="Número de cuenta del remitente (camt.053)")
    to_account: str = Field(..., min_length=10, max_length=24, description="Número de cuenta del destinatario (camt.053)")
    timestamp: datetime  # Fecha y hora de la transacción (camt.053)
    status: str = Field(..., pattern=r"^(pendiente|completada|fallida)$", description="Estado de la transacción (camt.053)")
    company_id: str = Field(..., description="ID de la empresa propietaria de la transacción")
    is_anomalous: Optional[bool] = False  # Indicador para anomalías

# Función para procesar el archivo CAMT.053
async def process_camt_file(file_path: str, company_id: str):
    """Procesa un archivo CAMT.053 y guarda las transferencias en la base de datos."""
    try:
        # Leer el archivo XML
        with open(file_path, 'r') as file:
            contents = file.read()

        tree = ET.ElementTree(ET.fromstring(contents))  # Parsear el XML
        root = tree.getroot()

        # Namespace para el XML
        ns = {'camt': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.08'}

        # Buscar las entradas (Ntry)
        entries = root.findall(".//camt:Ntry", ns)

        # Procesar cada entrada
        transfers = []
        for entry in entries:
            # Asegúrate de que los elementos existan antes de acceder a sus valores
            amount_element = entry.find(".//camt:Amt", ns)
            amount = float(amount_element.text) if amount_element is not None else 0.0

            currency_element = entry.find(".//camt:Amt", ns)
            currency = currency_element.attrib["Ccy"] if currency_element is not None else "EUR"

            from_account_element = entry.find(".//camt:DbtrAcct/camt:Id/camt:IBAN", ns)
            from_account = from_account_element.text if from_account_element is not None else "Desconocido"

            to_account_element = entry.find(".//camt:CdtrAcct/camt:Id/camt:IBAN", ns)
            to_account = to_account_element.text if to_account_element is not None else "ES1234123412341234"
            print(f"to_account: {to_account}")  # Verifica si es None

            status_element = entry.find(".//camt:Sts", ns)
            status = status_element.text if status_element is not None else "pendiente"

            timestamp_element = entry.find(".//camt:BookgDt/camt:DtTm", ns)
            timestamp = datetime.strptime(timestamp_element.text, "%Y-%m-%dT%H:%M:%S.%fZ") if timestamp_element is not None else datetime.now()

            # Crear una transferencia
            transfer = Transfer(
                id = uuid.uuid4(),  # Generamos un ID único
                amount=amount,
                currency=currency,
                from_account=from_account,
                to_account=to_account,
                timestamp=timestamp,
                status=status,
                company_id=company_id,  # Esto debe ser dinámico
                is_anomalous=False,  # Definir si es anómalo
            )
            transfers.append(transfer)

        # Insertar las transferencias en la base de datos
        if transfers:
            await db.transfers.insert_many([
            {
                **transfer.model_dump(),
                "id": Binary.from_uuid(transfer.id)  # Convertir UUID a Binary
            }
            for transfer in transfers
        ])

        logger.info(f"Se procesaron y guardaron {len(transfers)} transferencias correctamente.")
        return len(transfers)  # Número de transferencias procesadas

    except Exception as e:
        logger.error(f"Error al procesar el archivo {file_path}: {str(e)}")
        return 0
    
# Función principal para ejecutar el procesamiento de todos los archivos CAMT en la carpeta
async def process_all_camt_files(company_id: str):
    """Procesa todos los archivos CAMT.053 en la carpeta."""
    processed_count = 0
    for filename in os.listdir(CAMT_FOLDER):
        file_path = os.path.join(CAMT_FOLDER, filename)
        if filename.endswith(".xml"):  # Solo procesar archivos XML
            logger.info(f"Procesando archivo: {filename}")
            transfers_processed = await process_camt_file(file_path, company_id)
            processed_count += transfers_processed
            logger.info(f"{transfers_processed} transferencias procesadas del archivo {filename}")
    return processed_count

# Ejecución del script: llamada al procesamiento de todos los archivos
if __name__ == "__main__":
    # El company_id se puede pasar como argumento o configurarlo directamente
    company_id = "67dac86a1f2aeedf4d691dc4"  # Reemplaza con el ID de la empresa que deseas procesar
    import asyncio
    # Ejecutar el procesamiento en un bucle de eventos asincrónico
    asyncio.run(process_all_camt_files(company_id))
