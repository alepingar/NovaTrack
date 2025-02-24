import React, { useState, useEffect } from "react";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import MDBox from "components/MDBox";
import Grid from "@mui/material/Grid";
import axios from "axios";
import Footer from "examples/Footer";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";
import MDTypography from "components/MDTypography";
function GeneralDashboard() {
  const [transfers, setTransfers] = useState(0);
  const [transfersLastMonth, setTransfersLastMonth] = useState(0);
  const [anomaly, setAnomaly] = useState(0);
  const [anomalyLastMonth, setAnomalyLastMonth] = useState(0);
  const [amount, setAmount] = useState(0);
  const [amountLastMonth, setAmountLastMonth] = useState(0);
  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [transfersData, setTransfersData] = useState([]);
  const [anomaliesData, setAnomaliesData] = useState([]);
  useEffect(() => {
    const fetchData = async () => {
      try {
        const transfersRes = await axios.get(
          `http://127.0.0.1:8000/transfers/per-month/${year}/${month}`
        );
        setTransfers(transfersRes.data);

        const transfersLastMonthRes = await axios.get(
          `http://127.0.0.1:8000/transfers/per-month/${year}/${month - 1 || 12}`
        );
        setTransfersLastMonth(transfersLastMonthRes.data);

        const anomalyRes = await axios.get(
          `http://127.0.0.1:8000/transfers/anomaly/per-month/${year}/${month}`
        );
        setAnomaly(anomalyRes.data);

        const anomalyLastMonthRes = await axios.get(
          `http://127.0.0.1:8000/transfers/anomaly/per-month/${year}/${month - 1 || 12}`
        );
        setAnomalyLastMonth(anomalyLastMonthRes.data);

        const amountRes = await axios.get(
          `http://127.0.0.1:8000/transfers/amount/per-month/${year}/${month}`
        );
        setAmount(amountRes.data);

        const amountLastMonthRes = await axios.get(
          `http://127.0.0.1:8000/transfers/amount/per-month/${year}/${month - 1 || 12}`
        );
        setAmountLastMonth(amountLastMonthRes.data);

        const promises = [];
        for (let month = 1; month <= 12; month++) {
          promises.push(axios.get(`http://127.0.0.1:8000/transfers/per-month/${year}/${month}`));
        }
        const responses = await Promise.all(promises);
        const transfers = responses.map((response) => response.data);
        setTransfersData(transfers);

        const promisesA = [];
        for (let month = 1; month <= 12; month++) {
          promisesA.push(
            axios.get(`http://127.0.0.1:8000/transfers/anomaly/per-month/${year}/${month}`)
          );
        }
        const responses1 = await Promise.all(promisesA);
        const anomalies = responses1.map((response) => response.data);
        setAnomaliesData(anomalies);
      } catch (error) {
        console.log("Error fetching data", error);
      }
    };
    fetchData();
  }, [year, month]);

  const reportsGrowthChartData = {
    labels: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
    datasets: {
      label: "Transferencias",
      data: transfersData,
      fill: true,
      tension: 0.4,
    },
  };

  const reportsAnomaliesChartData = {
    labels: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
    datasets: {
      label: "Anomalías",
      data: anomaliesData,
      fill: true,
      tension: 0.4,
    },
  };

  const calculatePercentage = (previous, current) => {
    if (previous === 0) return { amount: current, color: "success" };
    const diff = current - previous;
    const percentage = ((diff / previous) * 100).toFixed(2);
    const isPositive = diff > 0;
    return {
      amount: isPositive ? `+${percentage}%` : `-${Math.abs(percentage)}%`,
      color: isPositive ? "success" : "error",
    };
  };

  const transfersChange = calculatePercentage(transfersLastMonth, transfers);
  const anomalyChange = calculatePercentage(anomalyLastMonth, anomaly);
  const amountChange = calculatePercentage(amountLastMonth, amount);

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        {/* Título de la sección de beneficios */}
        <MDBox mb={6} textAlign="center">
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
            <MDTypography variant="h6" fontWeight="medium">
              Detección de Anomalías en Tiempo Real
            </MDTypography>
            <MDTypography variant="body2" color="secondary">
              Nuestro sistema detecta anomalías de manera instantánea, asegurando que ninguna
              transacción sospechosa pase desapercibida.
            </MDTypography>
          </Grid>

          <Grid item xs={12} sm={4}>
            <MDTypography variant="h6" fontWeight="medium">
              Prevención de Fraudes con Algoritmos Avanzados
            </MDTypography>
            <MDTypography variant="body2" color="secondary">
              Utilizamos algoritmos de Machine Learning para prevenir fraudes antes de que ocurran.
            </MDTypography>
          </Grid>

          <Grid item xs={12} sm={4}>
            <MDTypography variant="h6" fontWeight="medium">
              Ahorro de Tiempo y Dinero al Automatizar la Seguridad
            </MDTypography>
            <MDTypography variant="body2" color="secondary">
              Al automatizar la detección de anomalías, ahorramos tiempo valioso y reducimos los
              costos asociados con la seguridad manual.
            </MDTypography>
          </Grid>
        </Grid>
      </MDBox>
      <MDBox py={3}>
        <MDBox mb={6} textAlign="center">
          <MDTypography variant="h4" fontWeight="bold">
            Estadísticas del mes
          </MDTypography>
          <MDTypography variant="body1" color="secondary">
            Resumen de las transferencias y anomalías detectadas durante el mes
          </MDTypography>
        </MDBox>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="dark"
                icon="sync_alt"
                title="Transferencias analizadas"
                count={transfers || 0}
                percentage={{
                  color: transfersChange.color,
                  amount: transfersChange.amount,
                  label: "Desde el último mes",
                }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} sm={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                icon="warning"
                title="Anomalías detectadas"
                count={anomaly || 0}
                percentage={{
                  color: anomalyChange.color,
                  amount: anomalyChange.amount,
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
                title="Cantidad transferida"
                count={`${amount.toLocaleString("es-ES") || 0}€`}
                percentage={{
                  color: amountChange.color,
                  amount: amountChange.amount,
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
                  date="Actualizado automáticamente"
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
                  description="Cantidad de anomalías detectadas a lo largo del año"
                  date="Actualizado automáticamente"
                  chart={reportsAnomaliesChartData}
                />
              </MDBox>
            </Grid>
          </Grid>
        </MDBox>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default GeneralDashboard;
