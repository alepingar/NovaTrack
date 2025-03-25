/** 
=========================================================
* Custom Footer
=========================================================
*/

// prop-types is a library for typechecking of props
import PropTypes from "prop-types";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// Material Dashboard 2 React base styles
import typography from "assets/theme/base/typography";

function Footer({ companyName }) {
  const { size } = typography;

  return (
    <MDBox
      component="footer"
      width="100%"
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      sx={{
        position: "fixed", // Lo coloca fijo al fondo de la página
        bottom: 0, // Lo ubica al fondo
        backgroundColor: "#f6f8fa",
        borderTop: "1px solid #e1e4e8",
        fontFamily: `"Segoe UI", "Helvetica Neue", Arial, sans-serif`,
        fontSize: size.sm,
        color: "#57606a",
        height: "auto", // El footer ahora se ajusta dinámicamente al contenido
        width: "100%",
        padding: "10px 0", // Espaciado del contenido
        marginTop: "auto", // Se asegura de que esté en el final cuando haya poco contenido
      }}
    >
      {/* Sección de derechos reservados */}
      <MDTypography sx={{ fontSize: "12px", color: "#57606a" }}>
        © {new Date().getFullYear()} {companyName}. Todos los derechos reservados.
      </MDTypography>

      {/* Enlaces más juntos */}
      <MDBox display="flex" flexDirection="row" gap={2} mt={1}>
        <MDTypography component="a" href="/terms" sx={linkStyle}>
          Términos
        </MDTypography>
        <MDTypography component="a" href="/privacy-policy" sx={linkStyle}>
          Privacidad
        </MDTypography>
        <MDTypography component="a" href="/support" sx={linkStyle}>
          Soporte
        </MDTypography>
        <MDTypography component="a" href="/about" sx={linkStyle}>
          Acerca de
        </MDTypography>
        <MDTypography component="a" href="/data_processing" sx={linkStyle}>
          Uso de datos personales
        </MDTypography>
      </MDBox>
    </MDBox>
  );
}

// Estilo para los links
const linkStyle = {
  color: "#57606a",
  textDecoration: "none",
  fontSize: "12px",
  "&:hover": { textDecoration: "underline" },
};

// Setting default values for the props of Footer
Footer.defaultProps = {
  companyName: "NovaTrack",
};

// Typechecking props for the Footer
Footer.propTypes = {
  companyName: PropTypes.string,
};

export default Footer;
