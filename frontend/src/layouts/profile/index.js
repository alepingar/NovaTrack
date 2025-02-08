/**
=========================================================
* Material Dashboard 2 React - v2.2.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-dashboard-react
* Copyright 2023 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

import React, { useEffect, useState } from "react";
import axios from "axios";
import Grid from "@mui/material/Grid";
import Divider from "@mui/material/Divider";
import Card from "@mui/material/Card";
import IconButton from "@mui/material/IconButton";
import EditIcon from "@mui/icons-material/Edit";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import PlatformSettings from "layouts/profile/components/PlatformSettings";

function CompanyProfile() {
  const [company, setCompany] = useState(null);
  const [formData, setFormData] = useState({});
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    const fetchCompanyData = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get("http://127.0.0.1:8000/companies/profile", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setCompany(response.data);
        setFormData(response.data);
      } catch (error) {
        console.error("Error al obtener los datos de la empresa:", error);
      }
    };

    fetchCompanyData();
  }, []);

  const handleEditToggle = () => {
    setIsEditing(!isEditing);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem("token");
      await axios.put("http://127.0.0.1:8000/companies/profile", formData, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setCompany(formData);
      setIsEditing(false);
      alert("Perfil actualizado correctamente");
    } catch (error) {
      console.error("Error al actualizar el perfil:", error);
      alert("Error al actualizar el perfil");
    }
  };

  if (!company) {
    return (
      <MDBox mt={5} textAlign="center">
        <MDTypography variant="h6" color="text">
          Cargando información...
        </MDTypography>
      </MDBox>
    );
  }

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox mb={2}>
        {/* Header */}
        <MDBox
          display="flex"
          alignItems="center"
          justifyContent="space-between"
          p={3}
          sx={{
            backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.3)), url("https://source.unsplash.com/random/1600x900")`,
            backgroundSize: "cover",
            backgroundPosition: "center",
            borderRadius: "lg",
            color: "white",
            height: "200px",
          }}
        >
          <MDBox>
            <MDTypography
              variant="h3"
              fontWeight="bold"
              sx={{ color: (theme) => theme.palette.text.primary }}
            >
              {company.name}
            </MDTypography>
            <MDTypography
              variant="h6"
              fontWeight="regular"
              sx={{ color: (theme) => theme.palette.text.secondary }}
            >
              {company.industry || "Industria no especificada"}
            </MDTypography>
          </MDBox>
        </MDBox>

        {/* Content */}
        <Grid container spacing={3} mt={2}>
          <Grid item xs={12} md={6} xl={4}>
            <PlatformSettings />
          </Grid>

          <Grid item xs={12} md={6} xl={4}>
            <Card sx={{ p: 3, borderRadius: "lg", boxShadow: 3 }}>
              <MDBox display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <MDTypography variant="h5" fontWeight="bold">
                  Información de la Empresa
                </MDTypography>
                <IconButton color="info" onClick={handleEditToggle}>
                  <EditIcon />
                </IconButton>
              </MDBox>
              <Grid container spacing={2}>
                {[
                  "name",
                  "email",
                  "industry",
                  "address",
                  "phone_number",
                  "website",
                  "country",
                  "tax_id",
                  "description",
                  "founded_date",
                ].map((field) => (
                  <Grid item xs={12} sm={6} key={field}>
                    <MDTypography variant="subtitle2" color="text">
                      {field.replace("_", " ").toUpperCase()}
                    </MDTypography>
                    {isEditing ? (
                      <MDInput
                        fullWidth
                        name={field}
                        value={formData[field] || ""}
                        onChange={handleChange}
                      />
                    ) : (
                      <MDTypography variant="body1" fontWeight="light">
                        {company[field] || "No especificado"}
                      </MDTypography>
                    )}
                  </Grid>
                ))}
              </Grid>
              {isEditing && (
                <MDBox mt={2} display="flex" justifyContent="flex-end" gap={2}>
                  <MDButton variant="outlined" color="secondary" onClick={handleEditToggle}>
                    Cancelar
                  </MDButton>
                  <MDButton variant="gradient" color="info" onClick={handleSubmit}>
                    Guardar Cambios
                  </MDButton>
                </MDBox>
              )}
            </Card>
          </Grid>
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default CompanyProfile;
