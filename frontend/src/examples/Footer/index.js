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
      flexDirection="row"
      justifyContent="space-around"
      alignItems="center"
      px={2}
      py={2}
      sx={{
        position: "relative", // Ahora se coloca después del contenido
        backgroundColor: "#f6f8fa",
        borderTop: "1px solid #e1e4e8",
        fontFamily: `"Segoe UI", "Helvetica Neue", Arial, sans-serif`,
        fontSize: size.sm,
        color: "#57606a",
        height: "50px",
        marginTop: "auto", // Se empuja al final cuando hay poco contenido
      }}
    >
      {/* Sección de derechos reservados */}
      <MDTypography sx={{ fontSize: "12px", color: "#57606a" }}>
        © {new Date().getFullYear()} {companyName}. Todos los derechos reservados.
      </MDTypography>

      {/* Enlaces más juntos */}
      <MDBox display="flex" flexDirection="row" gap={1}>
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
