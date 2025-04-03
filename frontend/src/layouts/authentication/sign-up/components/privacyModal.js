import React from "react";
import {
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Link,
  Paper,
} from "@mui/material";
import PropTypes from "prop-types";

function PrivacyModal({ open, onClose }) {
  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle> Política de Privacidad</DialogTitle>
      <DialogContent>
        <Paper elevation={6} sx={{ padding: 4 }}>
          <Divider sx={{ mb: 3 }} />

          <Typography variant="body1" paragraph>
            En nuestra plataforma, la privacidad y seguridad de tus datos son nuestra prioridad.
            Esta Esta Política de Privacidad describe cómo recopilamos, utilizamos y protegemos tu
            información personal al usar nuestros servicios. Al utilizar nuestra aplicación, las las
            las prácticas descritas en esta política.
          </Typography>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              1. Información que Recopilamos
            </Typography>
            <Typography variant="body1" paragraph>
              Recopilamos datos personales como nombre, dirección de correo electrónico, y otros
              detalles de la cuenta cuando te registras o usas la aplicación. También podemos
              recopilar información sobre tus transacciones financieras, como el monto, las
              involucradas, la fecha y hora, la ubicación y otros detalles relacionados con tus
              transferencias bancarias.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              2. Uso de la Información
            </Typography>
            <Typography variant="body1" paragraph>
              Usamos la información recopilada para brindarte una experiencia personalizada y
              nuestro nuestro servicio de detección de anomalías. Esto incluye analizar las
              transferencias financieras, detectar patrones inusuales y generar alertas en tiempo
              real. También utilizamos tus datos para fines de soporte al cliente, mejorar la
              seguridad de la plataforma, y cumplir con nuestras obligaciones legales.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              3. Protección de la Información
            </Typography>
            <Typography variant="body1" paragraph>
              Implementamos medidas de seguridad avanzadas para proteger tus datos personales de
              accesos no autorizados, alteraciones o divulgación. Sin embargo, ten en cuenta que
              ninguna medida de seguridad es completamente infalible. Utilizamos cifrado para la
              transmisión de información sensible, y almacenamos tus datos en seguros.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              4. Compartir Información con Terceros
            </Typography>
            <Typography variant="body1" paragraph>
              No compartimos tus datos personales con terceros, excepto en los siguientes casos:
            </Typography>
            <Typography variant="body1" paragraph>
              - Con proveedores de servicios que nos ayudan a operar la plataforma, como servicios
              de almacenamiento o análisis de datos.
            </Typography>
            <Typography variant="body1" paragraph>
              - Cuando sea necesario para cumplir con una obligación legal o para proteger los
              derechos, propiedad o seguridad de nuestra empresa, usuarios o el público.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              5. Tus Derechos sobre la Información
            </Typography>
            <Typography variant="body1" paragraph>
              Tienes el derecho de acceder, corregir, eliminar o restringir el uso de tus datos
              personales en cualquier momento. Para hacerlo, puedes contactarnos a través de correo
              electrónico. Además, puedes solicitar una copia de la información que tenemos sobre
              ti.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              6. Retención de Datos
            </Typography>
            <Typography variant="body1" paragraph>
              Conservamos tus datos personales durante el tiempo que sea necesario para cumplir los
              fines establecidos en esta política, o para cumplir con nuestras obligaciones legales,
              resolver disputas y hacer cumplir nuestros acuerdos.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              7. Cambios en la Política de Privacidad
            </Typography>
            <Typography variant="body1" paragraph>
              Nos reservamos el derecho de modificar esta Política de Privacidad en cualquier
              momento. Te notificaremos sobre cambios importantes a través de la plataforma o por
              correo electrónico. Es recomendable que revises periódicamente esta página para
              informado sobre cómo estamos protegiendo tu privacidad.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              8. Contacto
            </Typography>
            <Typography variant="body1" paragraph>
              Si tienes alguna pregunta o inquietud sobre nuestra Política de Privacidad o deseas
              ejercer tus derechos sobre tus datos personales, no dudes en ponerte en contacto con
              nosotros a través de nuestro correo electrónico:{" "}
              <Link href="mailto:novatracksupport@gmail.com">novatracksupport@gmail.com</Link>.
            </Typography>
          </Box>
        </Paper>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          Cerrar
        </Button>
      </DialogActions>
    </Dialog>
  );
}

PrivacyModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default PrivacyModal;
