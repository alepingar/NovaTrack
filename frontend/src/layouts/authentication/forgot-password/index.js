import { useState } from "react";
import axios from "axios";
import Card from "@mui/material/Card";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";
import BasicLayout from "layouts/authentication/components/BasicLayout"; // Importando BasicLayout

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:8000/auth/reset-password", { email });
      setMessage(response.data.message);
    } catch (error) {
      setMessage("Error: " + (error.response?.data?.detail || "Inténtalo de nuevo."));
    }
  };

  return (
    <BasicLayout>
      <Grid container style={{ height: "100vh" }}>
        {/* Columna izquierda: Fondo azul marino */}
        <Grid
          item
          xs={12}
          sm={6}
          display="flex"
          justifyContent="center"
          alignItems="center"
          style={{
            backgroundColor: "#2c3e50", // Azul marino
            paddingLeft: "0",
          }}
        ></Grid>
        <Grid
          item
          xs={12}
          sm={6}
          display="flex"
          justifyContent="center"
          alignItems="center"
          style={{ backgroundColor: "#2c3e50" }}
        >
          <Card
            style={{
              width: "100%",
              maxWidth: "100%",
              padding: "24px", // Fondo más oscuro para la tarjeta
            }}
          >
            <MDBox
              variant="gradient"
              bgColor="dark"
              borderRadius="lg"
              coloredShadow="info"
              mx={2}
              mt={-3}
              p={2}
              mb={1}
              textAlign="center"
            >
              <MDTypography variant="h4" fontWeight="medium" color="white" mt={1}>
                Recuperar Contraseña
              </MDTypography>
            </MDBox>
            <MDBox pt={4} pb={3} px={3}>
              <MDBox component="form" role="form" onSubmit={handleSubmit}>
                <MDBox mb={2}>
                  <MDInput
                    type="email"
                    label="Introduce tu correo"
                    fullWidth
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </MDBox>
                <MDBox mt={4} mb={1}>
                  <MDButton variant="gradient" color="dark" fullWidth type="submit">
                    Enviar
                  </MDButton>
                </MDBox>
                {message && (
                  <MDBox mt={3} mb={1} textAlign="center">
                    <MDTypography variant="body2" color="text" fontWeight="medium">
                      {message}
                    </MDTypography>
                  </MDBox>
                )}
              </MDBox>
            </MDBox>
          </Card>
        </Grid>
      </Grid>
    </BasicLayout>
  );
}

export default ForgotPassword;
