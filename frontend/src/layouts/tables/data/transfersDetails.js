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
  const [recurrentClients, setRecurrentClients] = useState(null); // Nuevo estado para clientes recurrentes
  const [companyIQR, setCompanyIQR] = useState(null); // Nuevo estado para el IQR de la empresa
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTransferDetails = async () => {
      try {
        const token = localStorage.getItem("token");
        // Obtener detalles de la transferencia
        const transferResponse = await axios.get(
          `${process.env.REACT_APP_API_URL}/transfers/${id}`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        setTransfer(transferResponse.data);

        const companyStatsResponse = await axios.get(
          `${process.env.REACT_APP_API_URL}/transfers/stats`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setCompanyStats(companyStatsResponse.data);
        setCompanyIQR({ low: companyStatsResponse.data?.q1, high: companyStatsResponse.data?.q3 });
        setRecurrentClients(companyStatsResponse.data?.recurrent_accounts);
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

  if (!transfer || !companyStats || !companyIQR || !recurrentClients) {
    return (
      <MDBox display="flex" justifyContent="center" alignItems="center" height="100vh">
        <MDTypography variant="h6" color="error">
          No se encontraron datos de la transferencia o de la empresa.
        </MDTypography>
      </MDBox>
    );
  }

  const getAnomalyReason = (transfer, companyStats, companyIQR, recurrentClients) => {
    let reason = [];
    const amountZscore =
      (transfer.amount - companyStats.mean) / (companyStats.std > 0 ? companyStats.std : 1);
    const transferHour = new Date(transfer.timestamp).getHours();

    const isOutsideIQR = transfer.amount < companyIQR.low || transfer.amount > companyIQR.high;
    const isRecurrentClient = recurrentClients.includes(transfer.from_account);

    // 1. Basado en el Z-score del Monto
    if (amountZscore > 3) {
      reason.push("Monto significativamente superior al promedio histórico de la empresa.");
    } else if (amountZscore < -3) {
      reason.push("Monto significativamente inferior al promedio histórico de la empresa.");
    } else if (amountZscore > 2 || amountZscore < -2) {
      reason.push("Monto inusual en comparación con el promedio histórico de la empresa.");
    }

    // 2. Hora de la Transferencia (considerando horas inusuales)
    if (transferHour < 7 || transferHour > 23) {
      reason.push(
        `Transferencia realizada en una hora muy inusual (${transferHour}:00 - ${
          transferHour + 1
        }:00) para la actividad general.`
      );
    } else if (transferHour < 9 || transferHour > 21) {
      reason.push(
        `Transferencia realizada en una hora fuera del horario comercial típico (${transferHour}:00 - ${
          transferHour + 1
        }:00).`
      );
    }

    // 3. Basado en el Rango Intercuartílico (IQR)
    if (isOutsideIQR) {
      reason.push(
        "El monto de la transferencia se encuentra fuera del rango intercuartílico (5%-95%) de las transacciones históricas de la empresa."
      );
    }

    // 4. Cliente Recurrente
    if (!isRecurrentClient) {
      reason.push(
        "La transferencia proviene de un cliente que no se identifica como recurrente en el historial de la empresa."
      );
    }

    // 5. Estado de la Transferencia
    if (transfer.status === "fallida") {
      reason.push("El estado de la transferencia es: Fallida.");
    }

    // Combinaciones de Razones (con enfoque en la hora y nuevas características)
    if (amountZscore > 2 && (transferHour < 9 || transferHour > 21)) {
      reason.push("Monto inusual realizado fuera del horario comercial típico.");
    }
    if (isOutsideIQR && (transferHour < 7 || transferHour > 23)) {
      reason.push("Monto fuera del rango típico transferido en una hora muy inusual.");
    }
    if (!isRecurrentClient && (transferHour < 9 || transferHour > 21)) {
      reason.push(
        "Transferencia de un cliente no recurrente realizada fuera del horario comercial típico."
      );
    }
    if (amountZscore > 2 && !isRecurrentClient) {
      reason.push("Monto inusual proveniente de un cliente no recurrente.");
    }
    if (isOutsideIQR && !isRecurrentClient) {
      reason.push("Monto fuera del rango típico realizado por un cliente no recurrente.");
    }

    // Razón genérica
    if (reason.length === 0 && transfer.is_anomalous) {
      reason.push("Anomalía detectada basada en una combinación de factores inusuales.");
    } else if (reason.length === 0 && !transfer.is_anomalous) {
      return "Transferencia normal.";
    }

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
                  {getAnomalyReason(transfer, companyStats, companyIQR, recurrentClients)}
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
