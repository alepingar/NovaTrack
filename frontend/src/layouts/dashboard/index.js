/**
=========================================================
* Material Dashboard 2 React - v2.2.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-dashboard-react
* Copyright 2023 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

import React, { useEffect, useState } from "react";
import axios from "axios";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";
import ReportsBarChart from "examples/Charts/BarCharts/ReportsBarChart";
import MDTypography from "components/MDTypography";

function Dashboard() {
  const [summary, setSummary] = useState({
    totalTransactions: 0,
    totalAnomalies: 0,
    totalAmount: 0,
  });

  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [summaryP, setSummaryP] = useState({
    totalTransfers: 0,
    totalAnomalies: 0,
    totalAmount: 0,
  });
  const [volumeByDay, setVolumeByDay] = useState([]);
  const [volumeAByDay, setVolumeAByDay] = useState([]);
  const [statusDistribution, setStatusDistribution] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("token");
      const headers = { Authorization: `Bearer ${token}` };

      try {
        const summaryRes = await axios.get("http://127.0.0.1:8000/transfers/summary-data", {
          headers,
        });
        setSummary(summaryRes.data);

        const summaryPRes = await axios.get(
          `http://127.0.0.1:8000/transfers/summary/per-month/${year}/${month}`,
          {
            headers,
          }
        );
        setSummaryP(summaryPRes.data);

        const volumeRes = await axios.get("http://127.0.0.1:8000/transfers/volume-by-day", {
          headers,
        });
        console.log(volumeRes.data);
        setVolumeByDay(volumeRes.data);

        const volumeARes = await axios.get(
          "http://127.0.0.1:8000/transfers/anomalous/volume-by-day",
          {
            headers,
          }
        );
        setVolumeAByDay(volumeARes.data);

        const statusRes = await axios.get("http://127.0.0.1:8000/transfers/status-distribution", {
          headers,
        });
        setStatusDistribution(statusRes.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [month, year]);

  const normalizeStatus = (status) =>
    status.trim().toLowerCase() === "completeda" ? "completada" : status.trim().toLowerCase();

  const normalizedStatusDistribution = statusDistribution.reduce((acc, item) => {
    const normalizedStatus = normalizeStatus(item.status);

    const existingIndex = acc.findIndex((entry) => entry.status === normalizedStatus);

    if (existingIndex !== -1) {
      acc[existingIndex].count += item.count;
    } else {
      acc.push({ status: normalizedStatus, count: item.count });
    }

    return acc;
  }, []);

  const reportsVolumeByDayChartData = {
    labels: volumeByDay.map((item) => item.date),
    datasets: {
      label: "Transferencias",
      data: volumeByDay.map((item) => item.count),
    },
  };

  const reportsVolumeAByDayChartData = {
    labels: volumeAByDay.map((item) => item.date),
    datasets: {
      label: "Anomalías",
      data: volumeAByDay.map((item) => item.count),
    },
  };

  const reportsStatusChartData = {
    labels: normalizedStatusDistribution.map((item) => item.status),
    datasets: {
      data: normalizedStatusDistribution.map((item) => item.count),
      label: "Distribución del estado de las Transacciones",
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

  const transfersChange = calculatePercentage(summaryP.totalTransfers, summary.totalTransactions);
  const anomalyChange = calculatePercentage(summaryP.totalAnomalies, summary.totalAnomalies);
  const amountChange = calculatePercentage(summaryP.totalAmount, summary.totalAmount);

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="dark"
                icon="sync_alt"
                title="Transferencias"
                count={summary.totalTransactions}
                percentage={{
                  color: transfersChange.color,
                  amount: transfersChange.amount,
                  label: "Desde el último mes",
                }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                icon="warning"
                title="Anomalías detectadas"
                count={summary.totalAnomalies}
                percentage={{
                  color: anomalyChange.color,
                  amount: anomalyChange.amount,
                  label: "Desde la última revisión",
                }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="success"
                icon="attach_money"
                title="Cantitad total transferida"
                count={`${summary.totalAmount.toLocaleString("es-ES")}€`}
                percentage={{
                  color: amountChange.color,
                  amount: amountChange.amount,
                  label: "En crecimiento",
                }}
              />
            </MDBox>
          </Grid>
        </Grid>
        <MDBox mt={4.5}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={6}>
              {/* Cada gráfico ocupa la mitad del espacio en pantallas medianas y grandes */}
              <MDBox mb={3}>
                <ReportsLineChart
                  color="info"
                  title="Crecimiento de transferencias"
                  description="Cantidad de transferencias analizadas a lo largo del año"
                  date="Actualizado hace 2 días"
                  chart={reportsVolumeByDayChartData}
                />
              </MDBox>
            </Grid>
            <Grid item xs={12} sm={6} md={6}>
              {/* Cada gráfico ocupa la mitad del espacio en pantallas medianas y grandes */}
              <MDBox mb={3}>
                <ReportsBarChart
                  color="primary"
                  title="Procesamiento de anomalías"
                  description="Distribución de anomalías por días"
                  date="Actualizado hace 4 días"
                  chart={reportsVolumeAByDayChartData}
                />
              </MDBox>
            </Grid>
          </Grid>
          <Grid container spacing={3}>
            {/* Gráfica de Distribución del Estado de las Transacciones */}
            <Grid item xs={12} sm={6} md={6}>
              <MDBox mt={4.5}>
                {statusDistribution.length > 0 ? (
                  <ReportsBarChart
                    color="error"
                    title="Distribución de estados de transacción"
                    description="Desglose de los diferentes estados de las transacciones"
                    date="Actualizado hace 5 días"
                    chart={reportsStatusChartData}
                  />
                ) : (
                  <MDTypography variant="caption" color="text">
                    No hay datos disponibles
                  </MDTypography>
                )}
              </MDBox>
            </Grid>
          </Grid>
        </MDBox>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Dashboard;
