import React from "react";
import { Divider, Container, Paper, Typography, Box, Link } from "@mui/material";

function TermsOfService() {
  return (
    <Box sx={{ display: "flex", justifyContent: "flex-start", mt: 4, ml: { xs: 3, md: 16 } }}>
      <Container maxWidth="lg">
        <Paper elevation={6} sx={{ padding: 4 }}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Términos y Condiciones
          </Typography>
          <Divider sx={{ mb: 3 }} />

          <Typography variant="body1" paragraph>
            Bienvenido a nuestra aplicación de Detección de Anomalías en Transferencias Bancarias.
            Estos términos y condiciones rigen el uso de nuestra plataforma y servicios. Al acceder
            y utilizar nuestra aplicación, aceptas cumplir con estos términos. Si no estás de
            acuerdo con ellos, te pedimos que no utilices nuestro servicio.
          </Typography>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              1. Aceptación de los Términos
            </Typography>
            <Typography variant="body1" paragraph>
              Al acceder o utilizar nuestra aplicación, aceptas cumplir con estos Términos de
              Servicio, incluyendo todas las políticas, regulaciones y disposiciones legales que se
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
              y regulaciones aplicables. No se permite el uso de la aplicación para realizar
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
              información sobre cómo manejamos tus datos personales y aseguramos la seguridad de la
              información.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              4. Exención de Responsabilidad
            </Typography>
            <Typography variant="body1" paragraph>
              Nuestra aplicación proporciona herramientas de detección de anomalías basadas en datos
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
              momento. Cualquier cambio será publicado en esta página, y te notificaremos sobre las
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
              que incumplas estos términos o realices actividades fraudulentas o no autorizadas. En
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
        </Paper>
      </Container>
    </Box>
  );
}

function PrivacyPolicy() {
  return (
    <Box sx={{ display: "flex", justifyContent: "flex-start", mt: 4, ml: { xs: 4, md: 8 } }}>
      <Container maxWidth="lg">
        <Paper elevation={6} sx={{ padding: 4 }}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Política de Privacidad
          </Typography>
          <Divider sx={{ mb: 3 }} />

          <Typography variant="body1" paragraph>
            En nuestra plataforma, la privacidad y seguridad de tus datos son nuestra prioridad.
            Esta Política de Privacidad describe cómo recopilamos, utilizamos y protegemos tu
            información personal al usar nuestros servicios. Al utilizar nuestra aplicación, aceptas
            las prácticas descritas en esta política.
          </Typography>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              1. Información que Recopilamos
            </Typography>
            <Typography variant="body1" paragraph>
              Recopilamos datos personales como nombre, dirección de correo electrónico, y otros
              detalles de la cuenta cuando te registras o usas la aplicación. También podemos
              recopilar información sobre tus transacciones financieras, como el monto, las cuentas
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
              mejorar nuestro servicio de detección de anomalías. Esto incluye analizar las
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
              ninguna medida de seguridad es completamente infalible. Utilizamos cifrado para
              proteger la transmisión de información sensible, y almacenamos tus datos en servidores
              seguros.
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
              personales en cualquier momento. Para hacerlo, puedes contactarnos a través de nuestro
              correo electrónico. Además, puedes solicitar una copia de la información que tenemos
              sobre ti.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              6. Retención de Datos
            </Typography>
            <Typography variant="body1" paragraph>
              Conservamos tus datos personales durante el tiempo que sea necesario para cumplir con
              los fines establecidos en esta política, o para cumplir con nuestras obligaciones
              legales, resolver disputas y hacer cumplir nuestros acuerdos.
            </Typography>
          </Box>

          <Box mt={2}>
            <Typography variant="h6" fontWeight="medium" gutterBottom>
              7. Cambios en la Política de Privacidad
            </Typography>
            <Typography variant="body1" paragraph>
              Nos reservamos el derecho de modificar esta Política de Privacidad en cualquier
              momento. Te notificaremos sobre cambios importantes a través de la plataforma o por
              correo electrónico. Es recomendable que revises periódicamente esta página para estar
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
              <Link href="mailto:support@financedetect.com">support@financedetect.com</Link>.
            </Typography>
          </Box>
        </Paper>
      </Container>
    </Box>
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
