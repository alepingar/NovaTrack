import React, { useEffect, useState } from "react";
import axios from "axios";
import { useParams, useNavigate } from "react-router-dom";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";

function TransferDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
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
    return (
      <MDBox display="flex" justifyContent="center" alignItems="center" height="100vh">
        <MDTypography variant="h6">Cargando detalles de la transferencia...</MDTypography>
      </MDBox>
    );
  }

  if (!transfer) {
    return (
      <MDBox display="flex" justifyContent="center" alignItems="center" height="100vh">
        <MDTypography variant="h6" color="error">
          No se encontró la transferencia con el ID {id}.
        </MDTypography>
      </MDBox>
    );
  }

  return (
    <MDBox pt={3} px={3}>
      <Card sx={{ marginLeft: "auto", marginRight: "auto", maxWidth: "70%", boxShadow: 3 }}>
        <CardContent>
          <MDTypography variant="h4" fontWeight="bold" mb={3}>
            Detalles de la Transferencia
          </MDTypography>
          <Table>
            <TableBody>
              {Object.entries({
                ID: transfer.id.slice(0, 8),
                Monto: `${transfer.amount} €`,
                "Cuenta Origen": transfer.from_account,
                "Fecha/Hora": new Date(transfer.timestamp).toLocaleString(),
                Descripción: transfer.description || "N/A",
                Categoría: transfer.category || "N/A",
                "Ubicación Origen": transfer.origin_location || "N/A",
                "Ubicación Destino": transfer.destination_location || "N/A",
                "Método de Pago": transfer.payment_method || "N/A",
                Estado: transfer.status,
                Usuario: transfer.user_identifier || "N/A",
                Recurrente: transfer.is_recurring ? "Sí" : "No",
                "IP Cliente": transfer.client_ip || "N/A",
                Tarifa: `${transfer.transaction_fee || 0}`,
                Anómala: transfer.is_anomalous ? "Sí" : "No",
                "Orden Vinculada": transfer.linked_order_id || "N/A",
              }).map(([key, value]) => (
                <TableRow key={key}>
                  <TableCell>
                    <MDTypography variant="subtitle2" fontWeight="medium">
                      {key}
                    </MDTypography>
                  </TableCell>
                  <TableCell>
                    <MDTypography variant="body2">{value}</MDTypography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <MDBox mt={3} display="flex" justifyContent="flex-end">
            <MDButton variant="outlined" color="secondary" onClick={() => navigate(-1)}>
              Volver
            </MDButton>
          </MDBox>
        </CardContent>
      </Card>
    </MDBox>
  );
}

export default TransferDetails;
