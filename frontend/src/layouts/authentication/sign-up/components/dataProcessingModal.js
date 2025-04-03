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

function DataProcessingModal({ open, onClose }) {
  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>Procesamiento de Datos</DialogTitle>
      <DialogContent>
        <Paper elevation={6} sx={{ padding: 4 }}>
          <Divider sx={{ mb: 3 }} />
          <Typography variant="body1" paragraph>
            En nuestra plataforma, nos tomamos muy en serio la protección de tus datos y estándares
            más altos de seguridad y cumplimiento de normativas, como el Reglamento Protección de
            Datos (GDPR).
          </Typography>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              1. ¿Cómo Usamos Tus Datos?
            </Typography>
            <Typography variant="body1" paragraph>
              Recopilamos datos de las transacciones bancarias de las empresas para detectar
              inusuales y prevenir fraudes. Estos datos incluyen información sobre el monto de
              transferencias, el remitente, la fecha y hora de la transacción, entre otros.
              Utilizamos estos datos para aplicar algoritmos de detección de anomalías basados
              machine learning.
            </Typography>
          </Box>
          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              2. Consentimiento para el Uso de los Datos (GDPR)
            </Typography>
            <Typography variant="body1" paragraph>
              Como parte de nuestro compromiso con la privacidad, solicitamos tu consentimiento
              antes de procesar cualquier dato personal. Este consentimiento nos permite tus datos
              tus datos para fines específicos de detección de fraude, en conformidad con el GDPR.
              con el GDPR. Puedes revisar y modificar tus preferencias en cualquier momento.
            </Typography>
          </Box>
          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              3. Seguridad de los Datos
            </Typography>
            <Typography variant="body1" paragraph>
              Nos aseguramos de que todos los datos sean almacenados y procesados de manera segura.
              Implementamos las últimas tecnologías de encriptación para proteger los datos durante
              su transmisión y almacenamiento. Además, solo personal autorizado tiene acceso a los
              datos.
            </Typography>
          </Box>
          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              4. ¿Cómo se Utilizan los Datos para la Detección de Fraude?
            </Typography>
            <Typography variant="body1" paragraph>
              Utilizamos los datos recopilados para alimentar modelos de detección de anomalías
              patrones sospechosos o inusuales en las transferencias. Estos modelos son entrenados
              entrenados con grandes volúmenes de datos históricos para identificar comportamientos
              fraudulentos, garantizando que solo las transacciones legítimas sean sean aprobadas.
            </Typography>
          </Box>
          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              5. ¿Qué Derechos Tienes Sobre Tus Datos?
            </Typography>
            <Typography variant="body1" paragraph>
              Tienes derecho a acceder, corregir o eliminar tus datos personales en cualquier
              momento. También momento. También puedes revocar tu consentimiento para el
              procesamiento de datos de manera sencilla. Estamos comprometidos con la transparencia
              y te damos control total sobre la información que compartes con nosotros.
            </Typography>
          </Box>
          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              6. Contacto y Más Información
            </Typography>
            <Typography variant="body1" paragraph>
              Si tienes alguna pregunta o inquietud sobre cómo procesamos tus datos, no dudes en{" "}
              <Link href="mailto:novatracksupport@gmail.com">contactarnos</Link>.
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

DataProcessingModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default DataProcessingModal;
