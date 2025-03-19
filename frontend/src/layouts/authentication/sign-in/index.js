import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Link } from "react-router-dom";
import Card from "@mui/material/Card";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";
import BasicLayout from "layouts/authentication/components/BasicLayout"; // Importando BasicLayout
import { useAuth } from "context/AuthContext";

function SignIn() {
  const [credentials, setCredentials] = useState({ email: "", password: "" });
  const [rememberMe, setRememberMe] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      navigate("/dashboard");
    }
  }, [navigate]);

  const handleSetRememberMe = () => setRememberMe(!rememberMe);

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:8000/auth/login", credentials);
      const { access_token } = response.data;

      login(access_token);
      alert("Inicio de sesión exitoso");

      navigate("/dashboard");
    } catch (error) {
      console.error("Error al iniciar sesión:", error.response?.data || error.message);
      if (error.response?.data?.detail) {
        alert(error.response.data.detail);
      } else {
        alert("Error al iniciar sesión. Verifique sus credenciales.");
      }
    }
  };

  return (
    <BasicLayout>
      <Grid container style={{ height: "100vh" }}>
        {/* Columna izquierda: Fondo azul marino con eslogan */}
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
                Iniciar Sesión
              </MDTypography>
            </MDBox>
            <MDBox pt={4} pb={3} px={3}>
              <MDBox component="form" role="form" onSubmit={handleSubmit}>
                <MDBox mb={2}>
                  <MDInput
                    type="email"
                    label="Correo Electrónico"
                    name="email"
                    fullWidth
                    value={credentials.email}
                    onChange={handleChange}
                    required
                  />
                </MDBox>
                <MDBox mb={2}>
                  <MDInput
                    type="password"
                    label="Contraseña"
                    name="password"
                    fullWidth
                    value={credentials.password}
                    onChange={handleChange}
                    required
                  />
                </MDBox>
                <MDBox display="flex" alignItems="center" ml={-1}>
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={handleSetRememberMe}
                    style={{ marginRight: "8px" }}
                  />
                  <MDTypography
                    variant="button"
                    fontWeight="regular"
                    color="text"
                    sx={{ cursor: "pointer", userSelect: "none" }}
                  >
                    Recordarme
                  </MDTypography>
                </MDBox>
                <MDBox mt={4} mb={1}>
                  <MDButton variant="gradient" color="dark" fullWidth type="submit">
                    Iniciar Sesión
                  </MDButton>
                </MDBox>
                <MDBox mt={3} mb={1} textAlign="center">
                  <MDTypography variant="button" color="text">
                    <MDTypography
                      component={Link}
                      to="/authentication/sign-up"
                      variant="button"
                      color="info"
                      fontWeight="medium"
                      textGradient
                    >
                      ¿No tienes una cuenta? Regístrate
                    </MDTypography>
                    <MDTypography
                      component={Link}
                      to="/forgot-password"
                      variant="button"
                      color="info"
                      fontWeight="medium"
                      textGradient
                    >
                      ¿Olvidaste tu contraseña?
                    </MDTypography>
                  </MDTypography>
                </MDBox>
              </MDBox>
            </MDBox>
          </Card>
        </Grid>
      </Grid>
    </BasicLayout>
  );
}

export default SignIn;
