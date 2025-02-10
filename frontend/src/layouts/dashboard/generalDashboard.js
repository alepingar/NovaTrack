import React, { useState, useEffect } from "react";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import MDBox from "components/MDBox";
import Grid from "@mui/material/Grid";

function GeneralDashboard() {
  const [summary, setSummary] = useState({
    totalTransfers: 0,
    totalAnomalies: 0,
    totalAmount: 0,
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const summaryRes = await fetch("http://127.0.0.1:8080/transfers/public/summary-data");
        setSummary(summaryRes);
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
                title="Transferencias totales"
                count={summary.totalTransfers}
                percentage={{
                  color: "success",
                  amount: "+5%",
                  label: "Desde la última semana",
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
