import React from "react";
import { Container, Typography, Box, Paper } from "@mui/material";

function TermsOfService() {
  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ padding: 4, marginTop: 4 }}>
        <Typography variant="h4" gutterBottom>
          Términos y Condiciones
        </Typography>
        <Typography variant="body1" paragraph>
          Bienvenido a nuestra aplicación. Estos términos y condiciones rigen el uso de nuestra
          plataforma...
        </Typography>
      </Paper>
    </Container>
  );
}

function PrivacyPolicy() {
  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ padding: 4, marginTop: 4 }}>
        <Typography variant="h4" gutterBottom>
          Política de Privacidad
        </Typography>
        <Typography variant="body1" paragraph>
          Nos tomamos la privacidad en serio. Aquí explicamos cómo gestionamos tus datos...
        </Typography>
      </Paper>
    </Container>
  );
}

function Support() {
  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ padding: 4, marginTop: 4 }}>
        <Typography variant="h4" gutterBottom>
          Soporte
        </Typography>
        <Typography variant="body1" paragraph>
          ¿Necesitas ayuda? Contáctanos a través de nuestro correo de soporte...
        </Typography>
      </Paper>
    </Container>
  );
}

function About() {
  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ padding: 4, marginTop: 4 }}>
        <Typography variant="h4" gutterBottom>
          Acerca de
        </Typography>
        <Typography variant="body1" paragraph>
          Somos una empresa que se dedica a...
        </Typography>
      </Paper>
    </Container>
  );
}

export { TermsOfService, PrivacyPolicy, Support, About };
