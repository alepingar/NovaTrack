import React, { useState, useEffect } from "react";
import axios from "axios";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import MDButton from "components/MDButton";
import MDTypography from "components/MDTypography";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

function SubscriptionUpgrade() {
  const [loading, setLoading] = useState(false);
  const [currentPlan, setCurrentPlan] = useState("");

  const plans = [
    {
      title: "Básico",
      price: "Gratis",
      description: "Hasta 20 archivos analizados al mes.",
      buttonText: "Mantener plan",
      buttonColor: "secondary",
      planId: "Basico",
      disabled: currentPlan === "BASICO" || currentPlan === "PRO",
    },
    {
      title: "Pro",
      price: "19,99€/mes",
      description: "Sin límite de archivos analizados.",
      buttonText: "Mejorar a Pro",
      buttonColor: "success",
      planId: "Pro",
      disabled: currentPlan === "PRO",
    },
  ];

  useEffect(() => {
    const fetchCurrentPlan = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/companies/get-current-plan", {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        });
        setCurrentPlan(response.data);
      } catch (error) {
        console.error("Error al obtener el plan actual:", error.response?.data || error);
      }
    };
    fetchCurrentPlan();
  }, []); // Se agrega el array vacío para evitar bucles de actualización

  const handleUpgrade = async (planId) => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      const response = await axios.post(
        "http://127.0.0.1:8000/companies/upgrade-plan",
        {},
        {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        }
      );
      // Redirigir a la URL de Stripe
      window.location.href = response.data.checkoutUrl;
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
          {plans.map((plan, index) => {
            let buttonText = "Elegir plan";

            if (currentPlan === plan.planId.toUpperCase()) {
              buttonText = "Plan actual";
            } else if (currentPlan === "BASICO" && plan.planId.toUpperCase() === "PRO") {
              buttonText = "Mejorar a Pro";
            } else {
              buttonText = "Elegir plan";
            }

            return (
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
                        onClick={() => handleUpgrade(plan.planId)}
                        disabled={plan.disabled || loading} // Deshabilitar si ya tienes el plan
                      >
                        {loading ? "Cargando..." : buttonText}
                      </MDButton>
                    </MDBox>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default SubscriptionUpgrade;
