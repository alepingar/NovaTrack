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
import ReportsBarChart from "examples/Charts/BarCharts/ReportsBarChart";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import PieChart from "examples/Charts/PieChart";
import MDTypography from "components/MDTypography";

function Dashboard() {
  const [summary, setSummary] = useState({
    totalTransactions: 0,
    totalAnomalies: 0,
    totalAmount: 0,
  });
  const [volumeByDay, setVolumeByDay] = useState([]);
  const [amountByCategory, setAmountByCategory] = useState([]);
  const [statusDistribution, setStatusDistribution] = useState([]);
  const [topOriginLocations, setTopOriginLocations] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("token");
      const headers = { Authorization: `Bearer ${token}` };

      try {
        const summaryRes = await axios.get("http://127.0.0.1:8000/transfers/summary-data", {
          headers,
        });
        setSummary(summaryRes.data);

        const volumeRes = await axios.get("http://127.0.0.1:8000/transfers/volume-by-day", {
          headers,
        });
        setVolumeByDay(volumeRes.data);

        const categoryRes = await axios.get("http://127.0.0.1:8000/transfers/amount-by-category", {
          headers,
        });
        setAmountByCategory(categoryRes.data);

        const statusRes = await axios.get("http://127.0.0.1:8000/transfers/status-distribution", {
          headers,
        });
        setStatusDistribution(statusRes.data);

        const locationRes = await axios.get(
          "http://127.0.0.1:8000/transfers/top-origin-locations",
          { headers }
        );
        setTopOriginLocations(locationRes.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

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
                title="Transfers"
                count={summary.totalTransactions}
                percentage={{
                  color: "success",
                  amount: "+5%",
                  label: "since last week",
                }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                icon="warning"
                title="Anomalies Detected"
                count={summary.totalAnomalies}
                percentage={{
                  color: "error",
                  amount: "+8%",
                  label: "since last check",
                }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="success"
                icon="attach_money"
                title="Total Amount Transferred"
                count={`$${summary.totalAmount.toLocaleString("es-ES")}`}
                percentage={{
                  color: "success",
                  amount: "+3%",
                  label: "growth rate",
                }}
              />
            </MDBox>
          </Grid>
        </Grid>
        <MDBox mt={4.5}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} lg={6}>
              <MDBox mb={3}>
                {volumeByDay.length > 0 ? (
                  <ReportsLineChart
                    color="info"
                    title="Transaction Volume by Day"
                    description="Overview of daily transactions"
                    date="Updated recently"
                    chart={{
                      labels: volumeByDay.map((d) => d.date),
                      datasets: [
                        {
                          label: "Transactions",
                          data: volumeByDay.map((d) => d.count),
                          backgroundColor: "rgba(75, 192, 192, 0.2)",
                          borderColor: "rgba(75, 192, 192, 1)",
                          borderWidth: 2,
                        },
                      ],
                    }}
                  />
                ) : (
                  <MDTypography variant="caption" color="text">
                    No data available
                  </MDTypography>
                )}
              </MDBox>
            </Grid>
            <Grid item xs={12} md={6} lg={6}>
              <MDBox mb={3}>
                {amountByCategory.length > 0 ? (
                  <PieChart
                    icon={{ color: "primary", component: "pie_chart" }}
                    title="Amount by Category"
                    description="Distribution of transaction amounts"
                    chart={{
                      labels: amountByCategory.map((d) => d.category),
                      datasets: [
                        {
                          data: amountByCategory.map((d) => d.amount),
                          backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
                        },
                      ],
                    }}
                  />
                ) : (
                  <MDTypography variant="caption" color="text">
                    No data available
                  </MDTypography>
                )}
              </MDBox>
            </Grid>
          </Grid>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} lg={6}>
              <MDBox mb={3}>
                {statusDistribution.length > 0 ? (
                  <PieChart
                    icon={{ color: "warning", component: "pie_chart" }}
                    title="Transaction Status Distribution"
                    description="Breakdown of transaction statuses"
                    chart={{
                      labels: statusDistribution.map((s) => s.status),
                      datasets: [
                        {
                          data: statusDistribution.map((s) => s.count),
                          backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
                        },
                      ],
                    }}
                  />
                ) : (
                  <MDTypography variant="caption" color="text">
                    No data available
                  </MDTypography>
                )}
              </MDBox>
            </Grid>
            <Grid item xs={12} md={6} lg={6}>
              <MDBox mb={3}>
                {topOriginLocations.length > 0 ? (
                  <ReportsBarChart
                    color="primary"
                    title="Top Origin Locations"
                    description="Most common transaction origins"
                    date="Updated just now"
                    chart={{
                      labels: topOriginLocations.map((loc) => loc.location),
                      datasets: [
                        {
                          label: "Count",
                          data: topOriginLocations.map((loc) => loc.count),
                          backgroundColor: "#82ca9d",
                        },
                      ],
                    }}
                  />
                ) : (
                  <MDTypography variant="caption" color="text">
                    No data available
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
