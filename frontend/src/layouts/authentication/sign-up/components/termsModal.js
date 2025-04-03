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

function TermsModal({ open, onClose }) {
  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
      <DialogTitle>Términos y Condiciones de Uso</DialogTitle>
      <DialogContent>
        <Paper style={{ maxHeight: "400px", overflow: "auto", padding: "16px" }}>
          {/* Aquí va el contenido de tus términos y condiciones */}
          <Divider sx={{ mb: 3 }} />

          <Typography variant="body1" paragraph>
            Bienvenido a nuestra aplicación de Detección de Anomalías en Transferencias Bancarias.
            Estos términos y condiciones rigen el uso de nuestra plataforma y servicios. Al acceder
            acceder y utilizar nuestra aplicación, aceptas cumplir con estos términos. Si acuerdo
            acuerdo con ellos, te pedimos que no utilices nuestro servicio.
          </Typography>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              1. Aceptación de los Términos
            </Typography>
            <Typography variant="body1" paragraph>
              Al acceder o utilizar nuestra aplicación, aceptas cumplir con estos Términos de
              Servicio, incluyendo todas las políticas, regulaciones y disposiciones legales que
              apliquen. Si no estás de acuerdo con alguna parte de los términos, debes dejar de
              utilizar nuestra aplicación inmediatamente.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              2. Uso Aceptable
            </Typography>
            <Typography variant="body1" paragraph>
              Debes utilizar nuestra aplicación solo para fines legales y conforme a todas las leyes
              leyes y regulaciones aplicables. No se permite el uso de la aplicación para realizar
              actividades fraudulentas, malintencionadas o que violen los derechos de otras
              personas.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              3. Privacidad y Seguridad de los Datos
            </Typography>
            <Typography variant="body1" paragraph>
              Tu privacidad es importante para nosotros. Consulta nuestra{" "}
              <Link href="/privacy-policy">Política de Privacidad</Link> para obtener más
              información sobre cómo manejamos tus datos personales y aseguramos la seguridad de
              información.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              4. Exención de Responsabilidad
            </Typography>
            <Typography variant="body1" paragraph>
              Nuestra aplicación proporciona herramientas de detección de anomalías basadas en
              financieros, pero no garantizamos que todas las transferencias detectadas sean
              fraudulentas o anómalas. No somos responsables de ninguna pérdida financiera, daño o
              perjuicio que puedas sufrir debido al uso de la aplicación.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              5. Modificaciones de los Términos
            </Typography>
            <Typography variant="body1" paragraph>
              Nos reservamos el derecho de modificar estos Términos de Servicio en cualquier
              momento. Cualquier cambio será publicado en esta página, y te notificaremos sobre
              actualizaciones significativas. El uso continuado de la aplicación después de tales
              modificaciones constituye tu aceptación de los nuevos términos.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              6. Suspensión o Terminación de la Cuenta
            </Typography>
            <Typography variant="body1" paragraph>
              Nos reservamos el derecho de suspender o terminar tu acceso a la aplicación en caso de
              de que incumplas estos términos o realices actividades fraudulentas o no tal caso, tal
              tal caso, podrías perder el acceso a tus datos o a otros servicios relacionados.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              7. Ley Aplicable
            </Typography>
            <Typography variant="body1" paragraph>
              Estos Términos de Servicio están regidos por las leyes del país en el que se
              proporciona este servicio, sin que se apliquen las normas sobre conflicto de leyes.
              Cualquier disputa derivada de estos términos será resuelta en los tribunales
              competentes.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              8. Contacto
            </Typography>
            <Typography variant="body1" paragraph>
              Si tienes alguna pregunta sobre estos Términos de Servicio o necesitas más
              información, no dudes en contactarnos a través de nuestro correo electrónico:{" "}
              <Link href="mailto:novatracksupport@gmail.com">novatracksupport@gmail.com</Link>.
            </Typography>
          </Box>
          {/* ... más contenido ... */}
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

TermsModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default TermsModal;
