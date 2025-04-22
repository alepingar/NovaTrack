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
import MDButton from "components/MDButton";
import Card from "@mui/material/Card";

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
  const [filterPeriod, setFilterPeriod] = useState("3months");
  const prevMonth = month === 1 ? 12 : month - 1;
  const prevYear = month === 1 ? year - 1 : year;

  useEffect(() => {
    const fetchData = async () => {
      try {
        const transfersRes = await axios.get(
          `${process.env.REACT_APP_API_URL}/transfers/per-month/${year}/${month}?period=${filterPeriod}`
        );
        setTransfers(transfersRes.data);

        const transfersLastMonthRes = await axios.get(
          `${process.env.REACT_APP_API_URL}/transfers/per-month/${prevYear}/${prevMonth}?period=${filterPeriod}`
        );
        setTransfersLastMonth(transfersLastMonthRes.data);

        const anomalyRes = await axios.get(
          `${process.env.REACT_APP_API_URL}/transfers/anomaly/per-month/${year}/${month}?period=${filterPeriod}`
        );
        setAnomaly(anomalyRes.data);

        const anomalyLastMonthRes = await axios.get(
          `${process.env.REACT_APP_API_URL}/transfers/anomaly/per-month/${prevYear}/${prevMonth}?period=${filterPeriod}`
        );
        setAnomalyLastMonth(anomalyLastMonthRes.data);

        const amountRes = await axios.get(
          `${process.env.REACT_APP_API_URL}/transfers/amount/per-month/${year}/${month}?period=${filterPeriod}`
        );
        setAmount(amountRes.data);

        const amountLastMonthRes = await axios.get(
          `${process.env.REACT_APP_API_URL}/transfers/amount/per-month/${prevYear}/${prevMonth}?period=${filterPeriod}`
        );
        setAmountLastMonth(amountLastMonthRes.data);

        const promises = [];
        const monthLabels = [];
        let startMonth = month;
        let startYear = year;
        let numMonths = 1;

        if (filterPeriod === "3months") {
          startMonth = month - 2;
          if (startMonth < 1) {
            startMonth = 12 + startMonth;
            startYear = year - 1;
          }
          numMonths = 3;
        } else if (filterPeriod === "year") {
          startMonth = 1;
          numMonths = 12;
        }

        for (let i = 0; i < numMonths; i++) {
          const currentMonth = ((startMonth + i - 1) % 12) + 1;
          const currentYear = startYear + Math.floor((startMonth + i - 1) / 12);

          promises.push(
            axios.get(
              `${process.env.REACT_APP_API_URL}/transfers/per-month/${currentYear}/${currentMonth}?period=month`
            )
          );
          monthLabels.push(
            new Date(currentYear, currentMonth - 1).toLocaleDateString("es-ES", {
              month: "short",
            })
          );
        }

        const responses = await Promise.all(promises);
        const transfers = responses.map((response) => response.data);
        setTransfersData(transfers);

        const promisesA = [];
        for (let i = 0; i < numMonths; i++) {
          const currentMonth = ((startMonth + i - 1) % 12) + 1;
          const currentYear = startYear + Math.floor((startMonth + i - 1) / 12);

          promisesA.push(
            axios.get(
              `${process.env.REACT_APP_API_URL}/transfers/anomaly/per-month/${currentYear}/${currentMonth}?period=month`
            )
          );
        }
        const responses1 = await Promise.all(promisesA);
        const anomalies = responses1.map((response) => response.data);
        setAnomaliesData(anomalies);
        setMonthLabels(monthLabels);
      } catch (error) {
        console.log("Error fetching data", error);
      }
    };

    fetchData();
  }, [year, month, filterPeriod]);

  const [monthLabels, setMonthLabels] = useState([
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
  ]);

  const handleFilterChange = (period) => {
    setFilterPeriod(period);
  };

  const getChartData = (data) => {
    return data;
  };

  const getFilteredChartData = (labels) => {
    return labels;
  };

  const reportsGrowthChartData = {
    labels: getFilteredChartData(monthLabels),
    datasets: {
      label: "Transferencias",
      data: getChartData(transfersData),
      fill: true,
      tension: 0.4,
    },
  };

  const reportsAnomaliesChartData = {
    labels: getFilteredChartData(monthLabels),
    datasets: {
      label: "Anomalías",
      data: getChartData(anomaliesData),
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

  const getStatisticsTitle = () => {
    switch (filterPeriod) {
      case "month":
        return "Estadísticas del último mes";
      case "3months":
        return "Estadísticas de los últimos 3 meses";
      case "year":
        return "Estadísticas del último año";
      default:
        return "Estadísticas";
    }
  };

  const testimonials = [
    {
      company: "TechCorp",
      quote:
        "Nuestro sistema ha mejorado significativamente la seguridad de nuestras transacciones. La detección de anomalías es precisa y nos ha ayudado a prevenir fraudes.",
      author: "Juan Pérez, Director Financiero",
    },
    {
      company: "Finance Solutions",
      quote:
        "La automatización de la detección de anomalías nos ha ahorrado tiempo y recursos. Estamos muy satisfechos con el rendimiento del sistema.",
      author: "María García, Gerente de Operaciones",
    },
    {
      company: "FarmaTech",
      quote:
        "La prevención de fraudes con algoritmos avanzados ha sido clave para proteger nuestras transacciones. Recomendamos este sistema a cualquier empresa que valore la seguridad.",
      author: "Carlos Rodríguez, CEO",
    },
  ];

  return (
    <DashboardLayout>
      <DashboardNavbar />

      {/* Sección: Beneficios y Características */}
      <MDBox py={3}>
        <Card sx={{ padding: 3, mb: 4 }}>
          <MDBox textAlign="center" mb={2}>
            <MDTypography variant="h4" fontWeight="bold">
              Beneficios y Características
            </MDTypography>
            <MDTypography variant="body1" color="secondary">
              Descubre cómo nuestro sistema puede ayudarte a proteger tus transacciones.
            </MDTypography>
          </MDBox>

          <Grid container spacing={3}>
            {/* Card 1: Detección de Anomalías */}
            <Grid item xs={12} sm={4} mt={3}>
              <MDTypography variant="h6" fontWeight="medium">
                Detección de Anomalías
              </MDTypography>
              <MDTypography variant="body2" color="secondary">
                Nuestro sistema detecta anomalías de manera instantánea, asegurando que ninguna
                transacción sospechosa pase desapercibida.
              </MDTypography>
            </Grid>

            {/* Card 2: Prevención de Fraudes */}
            <Grid item xs={12} sm={4} mt={3}>
              <MDTypography variant="h6" fontWeight="medium">
                Prevención de Fraudes con Algoritmos Avanzados
              </MDTypography>
              <MDTypography variant="body2" color="secondary">
                Utilizamos algoritmos de Machine Learning para prevenir fraudes antes de que
                ocurran.
              </MDTypography>
            </Grid>

            {/* Card 3: Ahorro de Tiempo y Costes */}
            <Grid item xs={12} sm={4} mt={3}>
              <MDTypography variant="h6" fontWeight="medium">
                Ahorro de Tiempo y Dinero al Automatizar la Seguridad
              </MDTypography>
              <MDTypography variant="body2" color="secondary">
                Al automatizar la detección de anomalías, ahorramos tiempo valioso y reducimos los
                costos asociados con la seguridad manual.
              </MDTypography>
            </Grid>
          </Grid>
        </Card>
      </MDBox>

      {/* Sección: Estadísticas de Actividad */}
      <Card sx={{ padding: 3, mb: 4 }}>
        <MDBox py={3}>
          <MDBox textAlign="center">
            <MDTypography variant="h4" fontWeight="bold">
              {getStatisticsTitle()}
            </MDTypography>
            <MDTypography variant="body1" color="secondary">
              Resumen de las transferencias y anomalías detectadas por la aplicación durante el
              período seleccionado.
            </MDTypography>
          </MDBox>
        </MDBox>

        {/* Filtros de estadísticas */}
        <MDBox py={3}>
          <MDBox mb={6} display="flex" justifyContent="space-between" alignItems="flex-start">
            <MDBox display="flex" flexDirection="column" alignItems="left">
              <MDTypography variant="caption" fontWeight="medium">
                Filtrar estadísticas por:
              </MDTypography>
              <MDBox mt={1} display="flex" gap={1}>
                <MDButton
                  variant={filterPeriod === "month" ? "contained" : "outlined"}
                  onClick={() => handleFilterChange("month")}
                >
                  <MDTypography variant="caption" fontWeight="medium">
                    Último mes
                  </MDTypography>
                </MDButton>
                <MDButton
                  variant={filterPeriod === "3months" ? "contained" : "outlined"}
                  onClick={() => handleFilterChange("3months")}
                >
                  <MDTypography variant="caption" fontWeight="medium">
                    Últimos 3 meses
                  </MDTypography>
                </MDButton>
                <MDButton
                  variant={filterPeriod === "year" ? "contained" : "outlined"}
                  onClick={() => handleFilterChange("year")}
                >
                  <MDTypography variant="caption" fontWeight="medium">
                    Último año
                  </MDTypography>
                </MDButton>
              </MDBox>
            </MDBox>
          </MDBox>

          {/* Tarjetas de estadísticas */}
          <Grid container spacing={3}>
            {/* Transferencias analizadas */}
            <Grid item xs={12} sm={6} lg={3}>
              <MDBox mb={1.5}>
                <ComplexStatisticsCard
                  color="dark"
                  icon="sync_alt"
                  title="Transferencias analizadas"
                  count={transfers || 0}
                  percentage={
                    filterPeriod !== "year"
                      ? {
                          color: transfersChange.color,
                          amount: transfersChange.amount,
                          label: "Desde el último mes",
                        }
                      : null
                  }
                />
              </MDBox>
            </Grid>

            {/* Anomalías detectadas */}
            <Grid item xs={12} sm={6} lg={3}>
              <MDBox mb={1.5}>
                <ComplexStatisticsCard
                  icon="warning"
                  title="Anomalías detectadas"
                  count={anomaly || 0}
                  percentage={
                    filterPeriod !== "year"
                      ? {
                          color: anomalyChange.color,
                          amount: anomalyChange.amount,
                          label: "Desde la última revisión",
                        }
                      : null
                  }
                />
              </MDBox>
            </Grid>

            {/* Monto total transferido */}
            <Grid item xs={12} sm={6} lg={3}>
              <MDBox mb={1.5}>
                <ComplexStatisticsCard
                  color="success"
                  icon="euro"
                  title="Cantidad transferida"
                  count={`${amount.toLocaleString("es-ES") || 0}€`}
                  percentage={
                    filterPeriod !== "year"
                      ? {
                          color: amountChange.color,
                          amount: amountChange.amount,
                          label: amountChange.amount > 0 ? "En crecimiento" : "En decrecimiento",
                        }
                      : null
                  }
                />
              </MDBox>
            </Grid>
          </Grid>

          {/* Gráficos de evolución */}
          <MDBox mt={8}>
            <Grid container spacing={3}>
              {/* Gráfico: Crecimiento de transferencias */}
              <Grid item xs={12} sm={6} md={6}>
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

              {/* Gráfico: Anomalías detectadas */}
              <Grid item xs={12} sm={6} md={6}>
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
      </Card>

      {/* Sección: Testimonios */}
      <Card sx={{ padding: 3, mb: 4 }}>
        <MDBox textAlign="center" mb={4}>
          <MDTypography variant="h4" fontWeight="bold">
            Opiniones de Empresas
          </MDTypography>
        </MDBox>
        <Grid container spacing={3}>
          {testimonials.map((testimonial, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card sx={{ p: 3, height: "100%" }}>
                <MDTypography variant="body1" fontWeight="medium" mb={2}>
                  “{testimonial.quote}”
                </MDTypography>
                <MDTypography variant="caption" color="secondary">
                  - {testimonial.author}, {testimonial.company}
                </MDTypography>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Card>

      <Footer />
    </DashboardLayout>
  );
}

export default GeneralDashboard;
