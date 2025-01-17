import React, { useEffect, useState } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";

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
        return <div className="text-center mt-5">Cargando transferencias...</div>;
    }

    return (
        <div className="container mt-4">
            <div className="card shadow">
                <div className="card-header bg-primary text-white">
                    <h3 className="mb-0">Transferencias Recibidas</h3>
                </div>
                <div className="card-body">
                    {transfers.length === 0 ? (
                        <div className="text-center text-muted">No se encontraron transferencias.</div>
                    ) : (
                        <table className="table table-hover">
                            <thead className="table-light">
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
                                    <tr key={transfer.id} className={transfer.is_anomalous ? "table-danger" : "table-default"}>
                                        <td>{transfer.id}</td>
                                        <td>{transfer.amount.toLocaleString("es-ES", { style: "currency", currency: "EUR" })}</td>
                                        <td>{transfer.from_account}</td>
                                        <td>{transfer.to_account}</td>
                                        <td>{new Date(transfer.timestamp).toLocaleString()}</td>
                                        <td>
                                            {transfer.is_anomalous ? (
                                                <span className="badge bg-danger">Sí</span>
                                            ) : (
                                                <span className="badge bg-success">No</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Transfers;
