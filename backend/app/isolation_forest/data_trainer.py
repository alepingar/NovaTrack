import random
import numpy as np

def generate_realistic_amount(avg_amount, anomaly=False):
    """
    Genera un monto realista para una transferencia bancaria.
    - avg_amount: Monto promedio de la empresa.
    - anomaly: Si es True, genera una anomalía (monto muy alto o muy bajo).
    """
    if anomaly:
        # 80% de las transferencias anómalas son extremas (mucho más altas o mucho más bajas)
        random_value = random.random()

        if random_value < 0.80:
            # Anomalía muy alta o muy baja
            anomaly_type = random.choice(["high", "low"])
            print(anomaly_type)
            if anomaly_type == "high":
                amount = round(random.lognormvariate(np.log(avg_amount * 2), 0.5), 2)  # Anomalía muy alta
            else:
                amount = round(random.uniform(0.01, avg_amount * 0.1), 2)  # Anomalía muy baja

        # 10% de las anomalías son moderadas (±50% del promedio)
        elif random_value < 0.90:
            amount = round(random.uniform(avg_amount * 0.5, avg_amount * 1.5), 2)  # Anomalía moderada

        # 10% de las anomalías son leves (±20% del promedio)
        else:
            amount = round(random.gauss(avg_amount, avg_amount * 0.2), 2)  # Anomalía leve

    else:
        # 80% de las transferencias normales son dentro de un rango de +/- 30% del promedio
        random_value = random.random()

        if random_value < 0.80:
            # Transferencias normales (dentro de +/- 30% de la media)
            amount = round(random.gauss(avg_amount, avg_amount * 0.3), 2)

        # 10% de las transferencias normales son dentro de un rango de +/- 50% del promedio
        elif random_value < 0.90:
            amount = round(random.uniform(avg_amount * 0.5, avg_amount * 1.5), 2)  # Transferencia más variable

        # 10% de las transferencias normales son un poco más altas o bajas
        else:
            amount = round(random.uniform(0.1, avg_amount * 2), 2)  # Rango más amplio

    # No permitir valores negativos
    amount = max(amount, 0.5)
    
    return amount

# Ejemplo: Empresa con montos promedio de 37€
for _ in range(100):
    kako = random.random()
    print("kako es" + str(kako))
    if kako > 0.9:
        anomaly = True
    else:
        anomaly = False
    print(generate_realistic_amount(37, anomaly))  # Anomalías
