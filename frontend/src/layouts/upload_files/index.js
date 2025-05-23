import React, { useState } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import MDButton from "components/MDButton";
import { Snackbar, Alert, CircularProgress } from "@mui/material";
import Tooltip from "@mui/material/Tooltip";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import axios from "axios";

function UploadFiles() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleFileUpload = async () => {
    if (!file) {
      setSnackbarMessage("Por favor, selecciona un archivo antes de subirlo.");
      setSnackbarOpen(true);
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      const headers = { Authorization: `Bearer ${token}` };

      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/transfers/upload-camt`,
        formData,
        {
          headers,
          timeout: 20000,
        }
      );

      setSnackbarMessage("Archivo cargado exitosamente.");
      setUploadSuccess(true);
    } catch (error) {
      console.error("Error uploading file:", error);

      // Si el backend envía un mensaje específico, lo mostramos
      if (error.response && error.response.data && error.response.data.detail) {
        setSnackbarMessage(error.response.data.detail);
      } else {
        setSnackbarMessage("Hubo un error al cargar el archivo.");
      }

      setUploadSuccess(false);
    } finally {
      setLoading(false);
      setSnackbarOpen(true);
    }
  };

  // Cerrar la notificación
  const handleSnackbarClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setSnackbarOpen(false);
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
                    Subir archivo CAMT.053
                    <Tooltip title="Para el correcto procesamiento del archivo, este deberá ser un extracto camt.053 en su última versión(v8.0) en formato .xml, si posee otro tipo de formato de extracto conviertalo antes de procesarlo.">
                      <HelpOutlineIcon fontSize="small" sx={{ ml: 1, cursor: "pointer" }} />
                    </Tooltip>
                  </MDTypography>
                </MDBox>
                <MDBox pt={3} px={2}>
                  <input
                    type="file"
                    accept=".xml"
                    onChange={handleFileChange}
                    style={{ marginBottom: "1rem" }}
                  />
                  <MDButton color="primary" onClick={handleFileUpload} disabled={loading}>
                    {loading ? <CircularProgress size={24} color="inherit" /> : "Subir archivo"}
                  </MDButton>
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
        <Alert
          onClose={handleSnackbarClose}
          severity={uploadSuccess ? "success" : "error"}
          sx={{ width: "100%" }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </DashboardLayout>
  );
}

export default UploadFiles;
