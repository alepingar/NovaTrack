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
      width="100%"
      display="flex"
      flexDirection={{ xs: "column", lg: "row" }}
      justifyContent="space-between"
      alignItems="center"
      px={1.5}
      py={2}
    >
      <MDBox
        display="flex"
        justifyContent="center"
        alignItems="center"
        flexWrap="wrap"
        color="text"
        fontSize={size.sm}
      >
        © {new Date().getFullYear()} {companyName}. Todos los derechos reservados.
      </MDBox>
    </MDBox>
  );
}

// Setting default values for the props of Footer
Footer.defaultProps = {
  companyName: "NovaTrack",
};

// Typechecking props for the Footer
Footer.propTypes = {
  companyName: PropTypes.string,
};

export default Footer;
