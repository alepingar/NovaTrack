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
import Footer from "examples/Footer";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";

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
          headers: { Authorization: `Bearer ${token}` },
        });
        console.log(response.data);
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

  const getAnomalyReason = (transfer) => {
    if (!transfer.features) return "Datos insuficientes para evaluar la anomalía.";
    const { is_banking_hour, amount_zscore } = transfer.features;
    if (amount_zscore > 10) {
      return "Monto extremadamente alto en comparación con el promedio.";
    }
    if (is_banking_hour === 0) {
      return "Transferencia fuera del horario bancario.";
    }
    return "Anomalía detectada sin causa específica.";
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox
        sx={{
          display: "flex",
          flexDirection: "column",
          flexGrow: 1,
          minHeight: "calc(100vh - 64px)",
          alignItems: "center",
          justifyContent: "center",
          p: 3,
        }}
      >
        <Card sx={{ maxWidth: "60%", boxShadow: 3 }}>
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
                  Estado: transfer.status,
                  Anómala: transfer.is_anomalous ? "Sí" : "No",
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
            {transfer.is_anomalous && (
              <MDBox mt={3} p={2} bgcolor="#ffebee" borderRadius="2px" boxShadow={1}>
                <MDTypography variant="h6" color="error" fontWeight="bold">
                  Motivo de la Anomalía
                </MDTypography>
                <MDTypography variant="body2">{getAnomalyReason(transfer)}</MDTypography>
              </MDBox>
            )}
            <MDBox mt={3} display="flex" justifyContent="flex-end">
              <MDButton variant="outlined" color="secondary" onClick={() => navigate(-1)}>
                Volver
              </MDButton>
            </MDBox>
          </CardContent>
        </Card>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default TransferDetails;
