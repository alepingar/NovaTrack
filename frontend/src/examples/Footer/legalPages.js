import React from "react";
import { Divider, Container, Paper, Typography, Box, Link } from "@mui/material";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

function TermsOfService() {
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <Box
        sx={{ display: "flex", justifyContent: "flex-start", mb: 5, mt: 4, ml: { xs: 3, md: 16 } }}
      >
        <Container maxWidth="lg">
          <Paper elevation={6} sx={{ padding: 4 }}>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Términos y Condiciones
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Typography variant="body1" paragraph>
              Bienvenido a nuestra aplicación de Detección de Anomalías en Transferencias Bancarias.
              Estos términos y condiciones rigen el uso de nuestra plataforma y servicios. Al
              acceder acceder y utilizar nuestra aplicación, aceptas cumplir con estos términos. Si
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
                Debes utilizar nuestra aplicación solo para fines legales y conforme a todas las
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
                Nos reservamos el derecho de suspender o terminar tu acceso a la aplicación en caso
                de que incumplas estos términos o realices actividades fraudulentas o no tal caso,
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
      <Footer />
    </DashboardLayout>
  );
}

function PrivacyPolicy() {
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <Box
        sx={{ display: "flex", justifyContent: "flex-start", mb: 5, mt: 4, ml: { xs: 4, md: 18 } }}
      >
        <Container maxWidth="lg">
          <Paper elevation={6} sx={{ padding: 4 }}>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Política de Privacidad
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Typography variant="body1" paragraph>
              En nuestra plataforma, la privacidad y seguridad de tus datos son nuestra prioridad.
              Esta Política de Privacidad describe cómo recopilamos, utilizamos y protegemos tu
              información personal al usar nuestros servicios. Al utilizar nuestra aplicación, las
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
                proteger la transmisión de información sensible, y almacenamos tus datos en seguros.
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
                personales en cualquier momento. Para hacerlo, puedes contactarnos a través de
                correo electrónico. Además, puedes solicitar una copia de la información que tenemos
                sobre ti.
              </Typography>
            </Box>

            <Box mt={2}>
              <Typography variant="h6" fontWeight="medium" gutterBottom>
                6. Retención de Datos
              </Typography>
              <Typography variant="body1" paragraph>
                Conservamos tus datos personales durante el tiempo que sea necesario para cumplir
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
        </Container>
      </Box>
      <Footer />
    </DashboardLayout>
  );
}

function Support() {
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <Box
        sx={{ display: "flex", justifyContent: "flex-start", mb: 5, mt: 4, ml: { xs: 4, md: 18 } }}
      >
        <Container maxWidth="lg">
          <Paper elevation={6} sx={{ padding: 4 }}>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Soporte
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Typography variant="body1" paragraph>
              ¿Tienes problemas o preguntas sobre nuestra plataforma? Estamos aquí para ayudarte. En
              esta sección, te proporcionamos información sobre cómo contactarnos, qué tipo de
              ofrecemos y qué recursos están disponibles para ayudarte a resolver cualquier
              inconveniente.
            </Typography>

            <Box mt={2}>
              <Typography variant="h6" fontWeight="medium" gutterBottom>
                1. Métodos de Contacto
              </Typography>
              <Typography variant="body1" paragraph>
                Si necesitas asistencia, puedes contactarnos de las siguientes formas:
              </Typography>
              <Typography variant="body1" paragraph>
                - **Correo electrónico**: Envíanos un correo a{" "}
                <Link href="mailto:novatracksupport@gmail.com">novatracksupport@gmail.com</Link>{" "}
                cualquier consulta general, dudas sobre la plataforma, o problemas técnicos.
              </Typography>
              <Typography variant="body1" paragraph>
                - **Teléfono**: También puedes llamarnos al número +1 (800) 123-4567 de lunes a
                viernes, de 9:00 a 18:00 (hora local).
              </Typography>
            </Box>

            <Box mt={2}>
              <Typography variant="h6" fontWeight="medium" gutterBottom>
                2. Tiempo de Respuesta
              </Typography>
              <Typography variant="body1" paragraph>
                Nuestro equipo de soporte está disponible para responder a tus consultas dentro de
                24 horas hábiles. Las solicitudes más complejas pueden tomar hasta 72 horas para ser
                resueltas.
              </Typography>
            </Box>

            <Box mt={2}>
              <Typography variant="h6" fontWeight="medium" gutterBottom>
                3. Soporte Técnico
              </Typography>
              <Typography variant="body1" paragraph>
                Si experimentas problemas técnicos, como errores en la aplicación o dificultades
                acceder a tu cuenta, por favor proporciona los siguientes detalles cuando nos
                contactes:
              </Typography>
              <Typography variant="body1" paragraph>
                - Descripción del problema.
              </Typography>
              <Typography variant="body1" paragraph>
                - Pasos previos que realizaste antes de que ocurriera el error.
              </Typography>
              <Typography variant="body1" paragraph>
                - Capturas de pantalla (si es posible) que muestren el error.
              </Typography>
            </Box>

            <Box mt={2}>
              <Typography variant="h6" fontWeight="medium" gutterBottom>
                4. Tiempos de Soporte
              </Typography>
              <Typography variant="body1" paragraph>
                Nuestro equipo de soporte está disponible de lunes a viernes, de 9:00 a 18:00 (hora
                local). Si tu solicitud es recibida fuera de estos horarios, nos pondremos en
                contigo tan pronto como sea posible.
              </Typography>
            </Box>

            <Box mt={2}>
              <Typography variant="h6" fontWeight="medium" gutterBottom>
                5. Políticas de Soporte
              </Typography>
              <Typography variant="body1" paragraph>
                Al utilizar nuestros servicios de soporte, aceptas nuestras políticas de servicio al
                cliente. Nos reservamos el derecho de priorizar los casos según su urgencia y la
                gravedad de los problemas técnicos. Apreciamos tu comprensión y paciencia.
              </Typography>
            </Box>

            <Box mt={3} display="flex" justifyContent="flex-end">
              <Typography variant="body1" paragraph>
                Si tienes alguna pregunta adicional o necesitas asistencia, no dudes en ponerte en
                contacto con nuestro equipo de soporte. ¡Estamos aquí para ayudarte!
              </Typography>
            </Box>
          </Paper>
        </Container>
      </Box>
      <Footer />
    </DashboardLayout>
  );
}

function About() {
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <Box
        sx={{ display: "flex", justifyContent: "flex-start", mb: 5, mt: 4, ml: { xs: 4, md: 18 } }}
      >
        <Container maxWidth="lg">
          <Paper elevation={6} sx={{ padding: 4 }}>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Acerca de
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Typography variant="body1" paragraph>
              Bienvenido a nuestra plataforma. En esta sección, te compartimos quiénes somos,
              misión, visión y los valores que guían el desarrollo de nuestra aplicación.
            </Typography>

            <Box mt={2}>
              <Typography variant="h6" fontWeight="medium" gutterBottom>
                1. Nuestra Misión
              </Typography>
              <Typography variant="body1" paragraph>
                Nuestra misión es ofrecer soluciones tecnológicas avanzadas para la detección de
                anomalías en transacciones financieras, mejorando la seguridad y eficiencia de las
                plataformas bancarias y financieras en todo el mundo.
              </Typography>
            </Box>

            <Box mt={2}>
              <Typography variant="h6" fontWeight="medium" gutterBottom>
                2. Nuestra Visión
              </Typography>
              <Typography variant="body1" paragraph>
                Queremos convertirnos en un líder global en la protección de transacciones
                financieras, utilizando las mejores herramientas de machine learning y big data para
                garantizar la integridad de los procesos bancarios y ofrecer un entorno seguro para
                todos los usuarios.
              </Typography>
            </Box>

            <Box mt={2}>
              <Typography variant="h6" fontWeight="medium" gutterBottom>
                3. Nuestro Equipo
              </Typography>
              <Typography variant="body1" paragraph>
                Somos un equipo de profesionales apasionados por la tecnología, la seguridad
                informática y el desarrollo de soluciones innovadoras. Nuestro equipo está compuesto
                por ingenieros, científicos de datos y expertos en finanzas, trabajando de manera
                colaborativa para llevar a cabo nuestra misión.
              </Typography>
            </Box>

            <Box mt={2}>
              <Typography variant="h6" fontWeight="medium" gutterBottom>
                4. Nuestros Valores
              </Typography>
              <Typography variant="body1" paragraph>
                - **Innovación**: Estamos comprometidos con la mejora continua y la implementación
                las últimas tecnologías en nuestros productos.
              </Typography>
              <Typography variant="body1" paragraph>
                - **Seguridad**: La protección de los datos de nuestros usuarios es nuestra máxima
                prioridad.
              </Typography>
              <Typography variant="body1" paragraph>
                - **Transparencia**: Operamos con honestidad y claridad, proporcionando a nuestros
                usuarios acceso completo a la información relevante sobre nuestros servicios.
              </Typography>
              <Typography variant="body1" paragraph>
                - **Compromiso**: Nos dedicamos a ofrecer un servicio de calidad excepcional,
                buscando la satisfacción del cliente.
              </Typography>
            </Box>

            <Box mt={2}>
              <Typography variant="h6" fontWeight="medium" gutterBottom>
                5. ¿Por Qué Elegirnos?
              </Typography>
              <Typography variant="body1" paragraph>
                Nuestro software utiliza algoritmos avanzados de machine learning y big data para
                detectar anomalías, lo que garantiza que las transacciones seguras y legítimas.
                legítimas. Estamos comprometidos con la mejora constante, y nuestra solución está
                solución está diseñada para adaptarse a las necesidades cambiantes de la industria
                financiera.
              </Typography>
            </Box>

            <Box mt={2}>
              <Typography variant="h6" fontWeight="medium" gutterBottom>
                6. Contacto
              </Typography>
              <Typography variant="body1" paragraph>
                Si deseas obtener más información sobre nuestra empresa, nuestros servicios, o
                colaborar con nosotros, no dudes en{" "}
                <Link href="mailto:novatracksupport@gmail.com">contactarnos</Link>.
              </Typography>
            </Box>
          </Paper>
        </Container>
      </Box>
      <Footer />
    </DashboardLayout>
  );
}

function DataProcessing() {
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <Box
        sx={{ display: "flex", justifyContent: "flex-start", mb: 5, mt: 4, ml: { xs: 4, md: 18 } }}
      >
        <Container maxWidth="lg">
          <Paper elevation={6} sx={{ padding: 4 }}>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Procesamiento de Datos
            </Typography>
            <Divider sx={{ mb: 3 }} />
            <Typography variant="body1" paragraph>
              En nuestra plataforma, nos tomamos muy en serio la protección de tus datos y
              estándares más altos de seguridad y cumplimiento de normativas, como el Reglamento
              Protección de Datos (GDPR).
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
                Nos aseguramos de que todos los datos sean almacenados y procesados de manera
                segura. Implementamos las últimas tecnologías de encriptación para proteger los
                datos durante su transmisión y almacenamiento. Además, solo personal autorizado
                tiene acceso a los datos.
              </Typography>
            </Box>
            <Box mt={2}>
              <Typography variant="h6" fontWeight="medium" gutterBottom>
                4. ¿Cómo se Utilizan los Datos para la Detección de Fraude?
              </Typography>
              <Typography variant="body1" paragraph>
                Utilizamos los datos recopilados para alimentar modelos de detección de anomalías
                patrones sospechosos o inusuales en las transferencias. Estos modelos son entrenados
                entrenados con grandes volúmenes de datos históricos para identificar
                comportamientos fraudulentos, garantizando que solo las transacciones legítimas sean
                sean aprobadas.
              </Typography>
            </Box>
            <Box mt={2}>
              <Typography variant="h6" fontWeight="medium" gutterBottom>
                5. ¿Qué Derechos Tienes Sobre Tus Datos?
              </Typography>
              <Typography variant="body1" paragraph>
                Tienes derecho a acceder, corregir o eliminar tus datos personales en cualquier
                momento. También momento. También puedes revocar tu consentimiento para el
                procesamiento de datos de manera sencilla. Estamos comprometidos con la
                transparencia y te damos control total sobre la información que compartes con
                nosotros.
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
        </Container>
      </Box>
      <Footer />
    </DashboardLayout>
  );
}

export { TermsOfService, PrivacyPolicy, Support, About, DataProcessing };
