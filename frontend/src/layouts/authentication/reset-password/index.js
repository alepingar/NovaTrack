import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import axios from "axios";
import Card from "@mui/material/Card";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";
import BasicLayout from "layouts/authentication/components/BasicLayout";

function ResetPassword() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (password.length < 8) {
      setMessage("La contraseña debe tener al menos 8 caracteres.");
      return;
    }

    if (password !== confirmPassword) {
      setMessage("Las contraseñas no coinciden.");
      return;
    }

    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/auth/reset-password-confirm`,
        {
          token,
          password,
        }
      );
      setMessage(response.data.message);
    } catch (error) {
      setMessage("Error: " + (error.response?.data?.detail || "Inténtalo de nuevo."));
    }
  };

  return (
    <BasicLayout>
      <Grid container style={{ height: "100vh" }}>
        <Grid
          item
          xs={12}
          sm={6}
          display="flex"
          justifyContent="center"
          alignItems="center"
          style={{ backgroundColor: "#2c3e50" }}
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
          <Card style={{ width: "100%", maxWidth: "100%", padding: "24px" }}>
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
                Restablecer Contraseña
              </MDTypography>
            </MDBox>
            <MDBox pt={4} pb={3} px={3}>
              <MDBox component="form" role="form" onSubmit={handleSubmit}>
                <MDBox mb={2}>
                  <MDInput
                    type="password"
                    label="Nueva contraseña"
                    fullWidth
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </MDBox>
                <MDBox mb={2}>
                  <MDInput
                    type="password"
                    label="Confirmar contraseña"
                    fullWidth
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                  />
                </MDBox>
                <MDBox mt={4} mb={1}>
                  <MDButton variant="gradient" color="dark" fullWidth type="submit">
                    Cambiar contraseña
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

export default ResetPassword;
