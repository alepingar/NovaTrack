import React, { useEffect, useState } from "react";
import axios from "axios";

function Transfers() {
    const [transfers, setTransfers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTransfers = async () => {
            try {
                const token = localStorage.getItem("token");
                const response = await axios.get("http://127.0.0.1:8000/companies/transfers", {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                setTransfers(response.data);
                setLoading(false);
            } catch (error) {
                console.error("Error al obtener las transferencias:", error);
                setLoading(false);
            }
        };

        fetchTransfers();
        const interval = setInterval(fetchTransfers, 5000); // Actualizar cada 5 segundos
        return () => clearInterval(interval); // Limpiar intervalo al desmontar
    }, []);

    if (loading) {
        return <p>Cargando transferencias...</p>;
    }

    return (
        <div className="container mt-4">
            <h2>Transferencias Recibidas</h2>
            <table className="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Monto</th>
                        <th>De</th>
                        <th>Para</th>
                        <th>Fecha</th>
                        <th>Anómala</th>
                    </tr>
                </thead>
                <tbody>
                    {transfers.map((transfer) => (
                        <tr key={transfer.id} className={transfer.is_anomalous ? "table-danger" : ""}>
                            <td>{transfer.id}</td>
                            <td>{transfer.amount}</td>
                            <td>{transfer.from_account}</td>
                            <td>{transfer.to_account}</td>
                            <td>{new Date(transfer.timestamp).toLocaleString()}</td>
                            <td>{transfer.is_anomalous ? "Sí" : "No"}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default Transfers;
