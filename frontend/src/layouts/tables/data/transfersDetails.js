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
  const [companyStats, setCompanyStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTransferDetails = async () => {
      try {
        const token = localStorage.getItem("token");
        // Obtener detalles de la transferencia
        const transferResponse = await axios.get(`http://127.0.0.1:8000/transfers/${id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        setTransfer(transferResponse.data);

        // Obtener estadísticas de la empresa
        const companyStatsResponse = await axios.get("http://127.0.0.1:8000/transfers/stats", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setCompanyStats(companyStatsResponse.data);
      } catch (error) {
        console.error("Error al obtener los datos:", error);
      } finally {
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

  if (!transfer || !companyStats) {
    return (
      <MDBox display="flex" justifyContent="center" alignItems="center" height="100vh">
        <MDTypography variant="h6" color="error">
          No se encontraron datos de la transferencia o de la empresa.
        </MDTypography>
      </MDBox>
    );
  }

  // Calcular amount_zscore en el frontend
  const amountMean = companyStats.mean;
  const amountStd = companyStats.std > 0 ? companyStats.std : 1; // Evitar división por 0
  const amountZscore = (transfer.amount - amountMean) / amountStd;

  // Verificar si la transferencia ocurrió en horario bancario
  const transferHour = new Date(transfer.timestamp).getHours();
  const isBankingHour = transferHour >= 8 && transferHour < 22 ? 1 : 0;

  const getAnomalyReason = (amountZscore, isBankingHour, amount, avgAmount, status) => {
    let reason = [];

    // Verificar monto extremadamente alto o bajo en comparación con el promedio
    if (amountZscore > 10) {
      reason.push("Monto extremadamente alto en comparación con el promedio.");
    } else if (amountZscore < -10) {
      reason.push("Monto extremadamente bajo en comparación con el promedio.");
    }

    if (isBankingHour === 0) {
      reason.push("Transferencia fuera del horario bancario (08:00 - 22:00).");
    }

    // Verificar si el monto está fuera del rango razonable para el tipo de transacción
    if (amount > avgAmount * 4) {
      reason.push("Monto excesivamente alto para la transacción.");
    } else if (amount < avgAmount * 0.1) {
      reason.push("Monto excesivamente bajo para la transacción.");
    }

    // Agregar el estado de la transferencia (si es fallida)
    if (status === "fallida") {
      reason.push("Estado de la transferencia: Fallida.");
    }

    // Si no se ha encontrado ninguna razón, se considera una anomalía sin causa específica
    if (reason.length === 0) {
      reason.push("Anomalía detectada sin causa específica.");
    }

    // Retornar las razones concatenadas
    return reason.join(" ");
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
                <MDTypography variant="body2">
                  {getAnomalyReason(
                    amountZscore,
                    isBankingHour,
                    transfer.amount,
                    amountMean,
                    transfer.status
                  )}
                </MDTypography>
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
