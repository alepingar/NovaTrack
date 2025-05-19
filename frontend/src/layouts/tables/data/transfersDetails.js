import React, { useEffect, useState, useCallback } from "react";
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
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";

function TransferDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [transfer, setTransfer] = useState(null);
  const [companyStats, setCompanyStats] = useState(null);
  const [recurrentClients, setRecurrentClients] = useState(null);
  const [companyIQR, setCompanyIQR] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);

  useEffect(() => {
    const fetchTransferDetails = async () => {
      try {
        const token = localStorage.getItem("token");
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

  const executeMarkAsNormal = useCallback(async () => {
    if (!transfer || !transfer.id) return;

    setIsUpdating(true);
    const token = localStorage.getItem("token");

    try {
      const response = await axios.patch(
        `${process.env.REACT_APP_API_URL}/transfers/mark-normal/${transfer.id}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setTransfer(response.data);
      console.log("Transferencia marcada como no anómala:", response.data);
    } catch (error) {
      console.error("Error al marcar la transferencia como no anómala:", error);
    } finally {
      setIsUpdating(false);
    }
  }, [transfer]);

  const handleOpenConfirmDialog = () => {
    setConfirmDialogOpen(true);
  };

  const handleCloseConfirmDialog = () => {
    setConfirmDialogOpen(false);
  };

  const handleConfirmAction = () => {
    handleCloseConfirmDialog();
    executeMarkAsNormal();
  };

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
        "La transferencia proviene de un cliente que no se identifica como recurrente en el historial de la empresa, junto con la apartición de patrones sospechosos."
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
            <MDBox mt={4} display="flex" justifyContent="space-between" alignItems="center">
              {transfer.is_anomalous && (
                <MDButton
                  variant="contained"
                  color="success"
                  onClick={handleOpenConfirmDialog}
                  disabled={isUpdating}
                >
                  Marcar como No Anómala
                </MDButton>
              )}
              {!transfer.is_anomalous && <MDBox sx={{ width: "1px" }} />}
              <MDButton
                variant="outlined"
                color="secondary"
                onClick={() => navigate(-1)}
                sx={{ ml: "auto" }}
              >
                Volver
              </MDButton>
            </MDBox>
          </CardContent>
        </Card>
      </MDBox>

      <Dialog
        open={confirmDialogOpen}
        onClose={handleCloseConfirmDialog}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">Confirmar Acción</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            ¿Estás seguro que quieres marcar la transferencia con ID {transfer?.id?.slice(0, 8)}{" "}
            como no anómala? Esta acción no se puede deshacer fácilmente.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <MDButton onClick={handleCloseConfirmDialog} color="secondary">
            Cancelar
          </MDButton>
          <MDButton
            onClick={handleConfirmAction}
            color="success"
            variant="contained"
            autoFocus
            disabled={isUpdating}
          >
            {isUpdating ? "Confirmando..." : "Confirmar"}
          </MDButton>
        </DialogActions>
      </Dialog>

      <Footer />
    </DashboardLayout>
  );
}

export default TransferDetails;
