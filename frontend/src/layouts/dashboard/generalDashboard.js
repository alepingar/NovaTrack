import React, { useState, useEffect } from "react";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import MDBox from "components/MDBox";
import Grid from "@mui/material/Grid";
import axios from "axios";

function GeneralDashboard() {
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
      } catch (error) {
        console.log("Error fetching data", error);
      }
    };

    fetchData();
  }, []);

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="dark"
                icon="sync_alt"
                title="Transferencias totales analizadas"
                count={summary.totalTransactions || 0}
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
                count={summary.totalAmount || 0}
                percentage={{
                  color: "success",
                  amount: "+3%",
                  label: "En crecimiento",
                }}
              />
            </MDBox>
          </Grid>
        </Grid>
      </MDBox>
    </DashboardLayout>
  );
}

export default GeneralDashboard;
