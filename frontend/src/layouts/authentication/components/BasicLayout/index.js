// prop-types is a library for typechecking of props
import PropTypes from "prop-types";

// @mui material components
import Grid from "@mui/material/Grid";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";

// Material Dashboard 2 React example components
import DefaultNavbar from "examples/Navbars/DefaultNavbar";
import PageLayout from "examples/LayoutContainers/PageLayout";

// Authentication pages components
import Footer from "layouts/authentication/components/Footer";

function BasicLayout({ children }) {
  return (
    <PageLayout>
      <DefaultNavbar />
      {/* Aquí ya no usamos la imagen, sino un fondo de color */}
      <MDBox
        position="absolute"
        width="100%"
        minHeight="100vh"
        sx={{
          backgroundColor: "#2c3e50", // Color de fondo sólido, puedes cambiarlo si quieres otro color
        }}
      />
      <MDBox px={1} width="100%" height="100vh" mx="auto">
        <Grid container spacing={1} justifyContent="center" alignItems="center" height="100%">
          <Grid item xs={12} sm={12} md={8} lg={7} xl={6}>
            {children}
          </Grid>
        </Grid>
      </MDBox>
      <Footer light />
    </PageLayout>
  );
}

// Eliminamos la propiedad `image` de las propTypes porque ya no la usamos
BasicLayout.propTypes = {
  children: PropTypes.node.isRequired,
};

export default BasicLayout;
