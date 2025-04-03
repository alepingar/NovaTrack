import React, { useState } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import DataTable from "examples/Tables/DataTable";
import transfersTableData from "layouts/tables/data/transfersTableData";
import MDButton from "components/MDButton";
import { Button, Snackbar, Alert } from "@mui/material";

function Tables() {
  const [filter, setFilter] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const { columns, rows, fetchFilteredData } = transfersTableData(filter);

  const handleFilter = async (range) => {
    setFilter(range);
    await fetchFilteredData(range);
    setSnackbarMessage(`Transferencias filtradas por ${getFilterMessage(range)}`);
    setSnackbarOpen(true);
  };

  const handleSnackbarClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setSnackbarOpen(false);
  };

  const getFilterMessage = (range) => {
    switch (range) {
      case "week":
        return "última semana";
      case "month":
        return "último mes";
      case "3months":
        return "últimos 3 meses";
      case "year":
        return "año";
      case "all":
        return "todas";
      default:
        return "";
    }
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox
        sx={{
          display: "flex",
          flexDirection: "column",
          flexGrow: 1,
          minHeight: "calc(100vh - 64px)",
        }}
      >
        <MDBox pt={6} pb={3}>
          <Grid container spacing={6}>
            <Grid item xs={12}>
              <Card>
                <MDBox
                  mx={2}
                  mt={-3}
                  py={3}
                  px={2}
                  variant="gradient"
                  bgColor="info"
                  borderRadius="lg"
                  coloredShadow="info"
                >
                  <MDTypography variant="h6" color="white">
                    Tabla de transferencias recibidas
                  </MDTypography>
                </MDBox>
                <MDBox pt={3} px={2}>
                  <MDButton onClick={() => handleFilter("week")}>Última Semana</MDButton>
                  <MDButton onClick={() => handleFilter("month")}>Último Mes</MDButton>
                  <MDButton onClick={() => handleFilter("3months")}>Últimos 3 Meses</MDButton>
                  <MDButton onClick={() => handleFilter("year")}>Todo el Año</MDButton>
                  <MDButton onClick={() => handleFilter("all")}>Todas</MDButton>
                </MDBox>
                <MDBox pt={3}>
                  <DataTable
                    table={{ columns, rows }}
                    isSorted={false}
                    entriesPerPage={false}
                    showTotalEntries={false}
                    noEndBorder
                  />
                </MDBox>
              </Card>
            </Grid>
          </Grid>
        </MDBox>
      </MDBox>
      <Footer />
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
      >
        <Alert onClose={handleSnackbarClose} severity="success" sx={{ width: "100%" }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </DashboardLayout>
  );
}

export default Tables;
