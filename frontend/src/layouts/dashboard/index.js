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
import PieChart from "examples/Charts/PieChart";
import MDTypography from "components/MDTypography";
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Pie,
  Cell,
  BarChart,
  Bar,
} from "recharts";

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

        if (amountByCategory.length === 0) {
          console.log("No hay datos en amountByCategory:", amountByCategory);
        } else {
          const categoryRes = await axios.get(
            "http://127.0.0.1:8000/transfers/amount-by-category",
            {
              headers,
            }
          );
          setAmountByCategory(categoryRes.data);
        }

        if (statusDistribution.length === 0) {
          console.log("No hay datos en statusDistribution:", statusDistribution);
        } else {
          const statusRes = await axios.get("http://127.0.0.1:8000/transfers/status-distribution", {
            headers,
          });
          setStatusDistribution(statusRes.data);
        }

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
                  <MDBox>
                    <MDTypography variant="h6" fontWeight="medium">
                      Transaction Volume by Day
                    </MDTypography>
                    <MDTypography variant="caption" color="text">
                      Overview of daily transactions
                    </MDTypography>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={volumeByDay}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="count" stroke="#8884d8" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </MDBox>
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
                  <MDBox>
                    <MDTypography variant="h6" fontWeight="medium">
                      Amount by Category
                    </MDTypography>
                    <MDTypography variant="caption" color="text">
                      Distribution of transaction amounts
                    </MDTypography>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={amountByCategory}
                          dataKey="amount"
                          nameKey="category"
                          cx="50%"
                          cy="50%"
                          outerRadius={100}
                        >
                          {amountByCategory.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={`hsl(${index * 40}, 70%, 50%)`} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </MDBox>
                ) : (
                  <MDTypography variant="caption" color="text">
                    No data available
                  </MDTypography>
                )}
              </MDBox>
            </Grid>
          </Grid>
          <Grid container spacing={3}>
            {/* Gráfica de Distribución del Estado de las Transacciones */}
            <Grid item xs={12} md={6} lg={6}>
              <MDBox mb={3}>
                {statusDistribution.length > 0 ? (
                  <MDBox>
                    <MDTypography variant="h6" fontWeight="medium">
                      Transaction Status Distribution
                    </MDTypography>
                    <MDTypography variant="caption" color="text">
                      Breakdown of transaction statuses
                    </MDTypography>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={statusDistribution}
                          dataKey="count"
                          nameKey="status"
                          cx="50%"
                          cy="50%"
                          outerRadius={100}
                          fill="#8884d8"
                        >
                          {statusDistribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={`hsl(${index * 40}, 70%, 50%)`} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </MDBox>
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
                  <MDBox>
                    <MDTypography variant="h6" fontWeight="medium">
                      Top Origin Locations
                    </MDTypography>
                    <MDTypography variant="caption" color="text">
                      Most common transaction origins
                    </MDTypography>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={topOriginLocations}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="location" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#82ca9d" />
                      </BarChart>
                    </ResponsiveContainer>
                  </MDBox>
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
