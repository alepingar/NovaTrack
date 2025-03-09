import React from "react";
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
  },
  {
    title: "Normal",
    price: "19,99€/mes",
    description: "Hasta 1000 transferencias analizadas con un modelo básico.",
    buttonText: "Elegir plan",
    buttonColor: "info",
  },
  {
    title: "Pro",
    price: "39,99€/mes",
    description: "Modelo avanzado sin límite de transferencias analizadas.",
    buttonText: "Mejorar a Pro",
    buttonColor: "success",
  },
];

function SubscriptionUpgrade() {
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox
        sx={{
          display: "flex",
          flexDirection: "column",
          flexGrow: 1, // Expande el contenido para empujar el footer
          minHeight: "calc(100vh - 64px)", // Ajusta al 100% menos la navbar
          alignItems: "center", // Centra el contenido
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
                    <MDButton color={plan.buttonColor} variant="contained">
                      {plan.buttonText}
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
