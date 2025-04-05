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

// @mui material components
import Grid from "@mui/material/Grid";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";

// Material Dashboard 2 React examples
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import MasterCard from "examples/Cards/MasterCard";
import DefaultInfoCard from "examples/Cards/InfoCards/DefaultInfoCard";
import axios from "axios";
// Billing page components
import Invoices from "layouts/billing/components/Invoices";
import React, { useEffect, useState } from "react";

function Billing() {
  const [company, setCompany] = useState(null);
  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [summaryP, setSummaryP] = useState({
    totalTransfers: 0,
    totalAnomalies: 0,
    totalAmount: 0,
  });

  useEffect(() => {
    const fetchCompanyData = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/companies/profile`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setCompany(response.data);

        const summaryPRes = await axios.get(
          `${process.env.REACT_APP_API_URL}/transfers/summary/per-month/${year}/${month}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        setSummaryP(summaryPRes.data);
      } catch (error) {
        console.error("Error al obtener los datos de la empresa:", error);
      }
    };

    fetchCompanyData();
  }, []);

  return (
    <DashboardLayout>
      <DashboardNavbar absolute isMini />
      <MDBox mt={8} sx={{ flexGrow: 1, minHeight: "calc(100vh - 64px)" }}>
        <MDBox mb={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} lg={8}>
              <Grid container spacing={3}>
                <Grid item xs={12} xl={6}>
                  <MasterCard
                    number={company ? company.billing_account_number : "Cargando..."}
                    holder={company ? company.name : "Cargando..."}
                  />
                </Grid>
                <Grid item xs={12} md={6} xl={3}>
                  <DefaultInfoCard
                    icon="account_balance"
                    title="Ingresos"
                    description="De los últimos 30 días"
                    value={`${summaryP.totalAmount}€`}
                  />
                </Grid>
                <Grid item xs={12} md={6} xl={3}>
                  <DefaultInfoCard
                    icon="subscriptions"
                    title="Suscripción actual"
                    description="Hasta el 30 de este mes"
                    value={company ? company.subscription_plan : "Cargando..."}
                  />
                </Grid>
              </Grid>
            </Grid>
            <Grid item xs={12} lg={4}>
              <Invoices />
            </Grid>
          </Grid>
        </MDBox>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Billing;
