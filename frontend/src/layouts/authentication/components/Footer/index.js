/**
=========================================================
* Custom Footer
=========================================================
*/

// prop-types is a library for typechecking of props
import PropTypes from "prop-types";

// @mui material components
import Container from "@mui/material/Container";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// Material Dashboard 2 React base styles
import typography from "assets/theme/base/typography";

function Footer({ light }) {
  const { size } = typography;

  return (
    <MDBox position="absolute" width="100%" bottom={0} py={2}>
      <Container>
        <MDBox
          width="100%"
          display="flex"
          justifyContent="center"
          alignItems="center"
          color={light ? "white" : "text"}
          fontSize={size.sm}
        >
          <MDTypography variant="caption" fontWeight="regular" color={light ? "white" : "dark"}>
            © {new Date().getFullYear()} NovaTrack. Todos los derechos reservados.
          </MDTypography>
        </MDBox>
      </Container>
    </MDBox>
  );
}

// Setting default props for the Footer
Footer.defaultProps = {
  light: false,
};

// Typechecking props for the Footer
Footer.propTypes = {
  light: PropTypes.bool,
};

export default Footer;
