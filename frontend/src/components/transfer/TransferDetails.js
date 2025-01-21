// TransferDetails.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import { useParams, useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";

function TransferDetails() {
    const { id } = useParams();         // Extraemos el ID de la URL
    const navigate = useNavigate();     // Para poder navegar de regreso u otras rutas
    const [transfer, setTransfer] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTransferDetails = async () => {
            try {
                const token = localStorage.getItem("token");
                const response = await axios.get(`http://127.0.0.1:8000/transfers/${id}`, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                setTransfer(response.data);
                setLoading(false);
            } catch (error) {
                console.error("Error al obtener los detalles de la transferencia:", error);
                setLoading(false);
            }
        };

        fetchTransferDetails();
    }, [id]);

    if (loading) {
        return <div className="text-center mt-5">Cargando detalles de la transferencia...</div>;
    }

    if (!transfer) {
        return <div className="text-center text-muted">No se encontró la transferencia con el ID {id}</div>;
    }

    return (
        <div className="container mt-4">
            <div className="card shadow">
                <div className="card-header bg-secondary text-white">
                    <h3 className="mb-0">Detalles de la Transferencia</h3>
                </div>
                <div className="card-body">
                    <table className="table table-bordered">
                        <tbody>
                            <tr>
                                <th>ID</th>
                                <td>{transfer.id}</td>
                            </tr>
                            <tr>
                                <th>Monto</th>
                                <td>{transfer.amount}</td>
                            </tr>
                            <tr>
                                <th>Moneda</th>
                                <td>{transfer.currency}</td>
                            </tr>
                            <tr>
                                <th>Cuenta Origen</th>
                                <td>{transfer.from_account}</td>
                            </tr>
                            <tr>
                                <th>Cuenta Destino</th>
                                <td>{transfer.to_account}</td>
                            </tr>
                            <tr>
                                <th>Fecha/Hora</th>
                                <td>{new Date(transfer.timestamp).toLocaleString()}</td>
                            </tr>
                            <tr>
                                <th>Descripción</th>
                                <td>{transfer.description || "N/A"}</td>
                            </tr>
                            <tr>
                                <th>Categoría</th>
                                <td>{transfer.category || "N/A"}</td>
                            </tr>
                            <tr>
                                <th>Ubicación Origen</th>
                                <td>{transfer.origin_location || "N/A"}</td>
                            </tr>
                            <tr>
                                <th>Ubicación Destino</th>
                                <td>{transfer.destination_location || "N/A"}</td>
                            </tr>
                            <tr>
                                <th>Método de Pago</th>
                                <td>{transfer.payment_method || "N/A"}</td>
                            </tr>
                            <tr>
                                <th>Estado</th>
                                <td>{transfer.status}</td>
                            </tr>
                            <tr>
                                <th>Usuario</th>
                                <td>{transfer.user_identifier || "N/A"}</td>
                            </tr>
                            <tr>
                                <th>Recurrente</th>
                                <td>{transfer.is_recurring ? "Sí" : "No"}</td>
                            </tr>
                            <tr>
                                <th>Device Fingerprint</th>
                                <td>{transfer.device_fingerprint || "N/A"}</td>
                            </tr>
                            <tr>
                                <th>IP Cliente</th>
                                <td>{transfer.client_ip || "N/A"}</td>
                            </tr>
                            <tr>
                                <th>ID Empresa</th>
                                <td>{transfer.company_id}</td>
                            </tr>
                            <tr>
                                <th>Tarifa</th>
                                <td>{transfer.transaction_fee || 0}</td>
                            </tr>
                            <tr>
                                <th>Anómala</th>
                                <td>{transfer.is_anomalous ? "Sí" : "No"}</td>
                            </tr>
                            <tr>
                                <th>Orden Vinculada</th>
                                <td>{transfer.linked_order_id || "N/A"}</td>
                            </tr>
                        </tbody>
                    </table>

                    {/* Botón para volver atrás */}
                    <button className="btn btn-secondary mt-3" onClick={() => navigate(-1)}>
                        Volver
                    </button>
                </div>
            </div>
        </div>
    );
}

export default TransferDetails;
