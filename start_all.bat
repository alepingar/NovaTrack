@echo off

:: Cambia al directorio de MongoDB y ejecuta el servidor
start cmd /k "mongod --dbpath C:\data\db"

:: Cambia al directorio de Kafka y ejecuta ZooKeeper
cd /d C:\kafka_2.13-3.9.0
start cmd /k ".\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties"

:: Espera 10 segundos para que Zookeeper esté completamente en ejecución
timeout /t 12 > nul

:: Ejecuta Kafka
cd /d C:\kafka_2.13-3.9.0
start cmd /k ".\bin\windows\kafka-server-start.bat .\config\server.properties"

:: Vuelve al directorio de NovaTrack y activa el entorno virtual
cd /d C:\Users\alexander\Desktop\NovaTrack
start cmd /k "venv\Scripts\activate && cd backend && uvicorn app.main:app --reload"

:: Inicia el frontend
cd /d C:\Users\alexander\Desktop\NovaTrack
start cmd /k "cd frontend && npm start"

:: Ejecuta el consumidor de Kafka
cd /d C:\Users\alexander\Desktop\NovaTrack
start cmd /k "venv\Scripts\activate && cd backend && python -m app.kafka.consumer"

:: Ejecuta el script de transferencias aleatorias
cd /d C:\Users\alexander\Desktop\NovaTrack
start cmd /k "venv\Scripts\activate && python backend/app/kafka/random_transfers_producer.py"

: : cd C:\Users\alexander\Desktop\NovaTrack