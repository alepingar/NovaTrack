import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { Box, Button, Typography, CircularProgress, Card, CardContent } from "@mui/material";

function ConfirmPayment() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleConfirmPayment = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      await axios.post(
        "http://127.0.0.1:8000/companies/confirm-plan",
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      alert("Pago confirmado con éxito.");
      navigate("/dashboard"); // Redirige al dashboard después del pago
    } catch (error) {
      console.error("Error al confirmar el pago:", error.response?.data || error);
      alert("Error al confirmar el pago. Por favor, inténtalo de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    navigate("/subscriptions");
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      height="100vh"
      bgcolor="#f8f9fa"
    >
      <Card sx={{ width: 400, textAlign: "center", p: 3 }}>
        <CardContent>
          <Typography variant="h5" fontWeight="bold" gutterBottom>
            Confirmar Pago
          </Typography>
          <Typography variant="body1" color="textSecondary" mb={3}>
            ¿Deseas confirmar tu suscripción al plan PRO?
          </Typography>
          {loading ? (
            <CircularProgress />
          ) : (
            <Box display="flex" justifyContent="space-between" mt={2}>
              <Button variant="contained" color="error" onClick={handleCancel}>
                Cancelar
              </Button>
              <Button variant="contained" color="success" onClick={handleConfirmPayment}>
                Confirmar Pago
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}

export default ConfirmPayment;
