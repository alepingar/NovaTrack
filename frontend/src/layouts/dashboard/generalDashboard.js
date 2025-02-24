import React, { useState, useEffect } from "react";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import MDBox from "components/MDBox";
import Grid from "@mui/material/Grid";
import axios from "axios";
import reportsGrowthChartData from "./data/reportsGrowthChartData";
import reportsAnomaliesChartData from "./data/reportsAnomaliesChartData";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";
import MDTypography from "components/MDTypography";
function GeneralDashboard() {
  const [transfers, setTransfers] = useState(0);

  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);

  const [summary, setSummary] = useState({
    totalTransactions: 0,
    totalAnomalies: 0,
    totalAmount: 0,
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const summaryRes = await axios.get("http://127.0.0.1:8000/transfers/public/summary-data");
        setSummary(summaryRes.data);
        const transfersRes = await axios.get(
          `http://127.0.0.1:8000/transfers/per-month/${year}/${month}`
        );
        setTransfers(transfersRes.data);
      } catch (error) {
        console.log("Error fetching data", error);
      }
    };
    fetchData();
  }, [year, month]);

  const reportsGrowthChartData = {
    labels: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
    datasets: { label: "Transferencias", data: [10, 25, 37, 52, 60, 54, 65, 71, 79, 86, 92, 102] },
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        {/* Título de la sección de beneficios */}
        <MDBox mb={3} textAlign="center">
          <MDTypography variant="h4" fontWeight="bold">
            Beneficios y Características
          </MDTypography>
          <MDTypography variant="body1" color="secondary">
            Descubre cómo nuestro sistema puede ayudarte a proteger tus transacciones.
          </MDTypography>
        </MDBox>

        {/* Contenedor de los beneficios */}
        <Grid container spacing={3}>
          <Grid item xs={12} sm={4}>
            <MDBox
              p={3}
              borderRadius="lg"
              shadow="sm"
              sx={{ backgroundColor: "#f4f6f8", textAlign: "center" }}
            >
              <MDTypography variant="h6" fontWeight="medium">
                Detección de Anomalías en Tiempo Real
              </MDTypography>
              <MDTypography variant="body2" color="secondary">
                Nuestro sistema detecta anomalías de manera instantánea, asegurando que ninguna
                transacción sospechosa pase desapercibida.
              </MDTypography>
            </MDBox>
          </Grid>

          <Grid item xs={12} sm={4}>
            <MDBox
              p={3}
              borderRadius="lg"
              shadow="sm"
              sx={{ backgroundColor: "#f4f6f8", textAlign: "center" }}
            >
              <MDTypography variant="h6" fontWeight="medium">
                Prevención de Fraudes con Algoritmos Avanzados
              </MDTypography>
              <MDTypography variant="body2" color="secondary">
                Utilizamos algoritmos de Machine Learning para prevenir fraudes antes de que
                ocurran.
              </MDTypography>
            </MDBox>
          </Grid>

          <Grid item xs={12} sm={4}>
            <MDBox
              p={3}
              borderRadius="lg"
              shadow="sm"
              sx={{ backgroundColor: "#f4f6f8", textAlign: "center" }}
            >
              <MDTypography variant="h6" fontWeight="medium">
                Ahorro de Tiempo y Dinero al Automatizar la Seguridad
              </MDTypography>
              <MDTypography variant="body2" color="secondary">
                Al automatizar la detección de anomalías, ahorramos tiempo valioso y reducimos los
                costos asociados con la seguridad manual.
              </MDTypography>
            </MDBox>
          </Grid>
        </Grid>
      </MDBox>
      <MDBox py={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="dark"
                icon="sync_alt"
                title="Transferencias totales analizadas este mes"
                count={transfers || 0}
                percentage={{
                  color: "success",
                  amount: "+5%",
                  label: "Desde la última semana",
                }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} sm={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                icon="warning"
                title="Anomalías detectadas"
                count={summary.totalAnomalies || 0}
                percentage={{
                  color: "error",
                  amount: "+8%",
                  label: "Desde la última revisión",
                }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} sm={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="success"
                icon="warning"
                title="Cantidad total transferida"
                count={`${summary.totalAmount.toLocaleString("es-ES") || 0}€`}
                percentage={{
                  color: "success",
                  amount: "+3%",
                  label: "En crecimiento",
                }}
              />
            </MDBox>
          </Grid>
        </Grid>
        <MDBox mt={8}>
          <Grid container spacing={3}>
            {" "}
            {/* Espaciado entre los elementos */}
            <Grid item xs={12} sm={6} md={6}>
              {" "}
              {/* Cada gráfico ocupa la mitad del espacio en pantallas medianas y grandes */}
              <MDBox mb={3}>
                <ReportsLineChart
                  color="info"
                  title="Crecimiento de transferencias"
                  description="Cantidad de transferencias analizadas a lo largo del año"
                  date="Actualizado hace 2 días"
                  chart={reportsGrowthChartData}
                />
              </MDBox>
            </Grid>
            <Grid item xs={12} sm={6} md={6}>
              {" "}
              {/* El segundo gráfico también ocupa la mitad */}
              <MDBox mb={3}>
                <ReportsLineChart
                  color="error"
                  title="Anomalías detectadas"
                  description="Cantidad de anomalías detectadas a lo largo de la semana"
                  date="Actualizado hace 5 días"
                  chart={reportsAnomaliesChartData}
                />
              </MDBox>
            </Grid>
          </Grid>
        </MDBox>
      </MDBox>
    </DashboardLayout>
  );
}

export default GeneralDashboard;
