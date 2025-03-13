import React, { useState } from "react";
import axios from "axios"; // Importamos Axios
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import MDButton from "components/MDButton";
import MDTypography from "components/MDTypography";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

const plans = [
  {
    title: "Básico",
    price: "Gratis",
    description: "Hasta 100 transferencias analizadas con un modelo básico.",
    buttonText: "Mantener plan",
    buttonColor: "secondary",
    planId: "Basico",
  },
  {
    title: "Normal",
    price: "19,99€/mes",
    description: "Hasta 1000 transferencias analizadas con un modelo básico.",
    buttonText: "Elegir plan",
    buttonColor: "info",
    planId: "Normal",
  },
  {
    title: "Pro",
    price: "39,99€/mes",
    description: "Modelo avanzado sin límite de transferencias analizadas.",
    buttonText: "Mejorar a Pro",
    buttonColor: "success",
    planId: "Pro",
  },
];

function SubscriptionUpgrade() {
  const [loading, setLoading] = useState(false);

  const handleUpgrade = async (planId) => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      const headers = { Authorization: `Bearer ${token}` };
      const response = await axios.put(
        `http://127.0.0.1:8000/companies/upgrade-plan/${planId}`,
        null,
        { headers }
      );
      setLoading(false);
    } catch (error) {
      console.error("Error al actualizar el plan:", error.response?.data || error);
      setLoading(false);
    }
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
        <Grid container justifyContent="center" spacing={3}>
          {plans.map((plan, index) => (
            <Grid item xs={12} md={6} lg={4} key={index}>
              <Card>
                <CardContent>
                  <MDBox textAlign="center" py={2}>
                    <MDTypography variant="h5" fontWeight="bold">
                      {plan.title}
                    </MDTypography>
                    <MDTypography variant="h6" color="primary">
                      {plan.price}
                    </MDTypography>
                    <MDTypography variant="body2" mt={1} mb={3}>
                      {plan.description}
                    </MDTypography>
                    <MDButton
                      color={plan.buttonColor}
                      variant="contained"
                      onClick={() => handleUpgrade(plan.planId.toUpperCase())}
                      disabled={loading} // Deshabilitar el botón mientras carga
                    >
                      {loading ? "Cargando..." : plan.buttonText} {/* Mostrar texto de loading */}
                    </MDButton>
                  </MDBox>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default SubscriptionUpgrade;
