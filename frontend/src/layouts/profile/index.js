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
  const [errors, setErrors] = useState({});

  useEffect(() => {
    const fetchCompanyData = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/companies/profile`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        const companyData = response.data;

        if (companyData.founded_date) {
          companyData.founded_date = companyData.founded_date.split("T")[0];
        }
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

  const validateForm = () => {
    const newErrors = {};
    const phoneRegex = /^[0-9]{9}$/; // A simple regex for 10-digit phone number validation
    const emailRegex = /^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$/; // Regex for valid email format
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/; // Simple date format YYYY-MM-DD

    if (formData.phone_number && !phoneRegex.test(formData.phone_number)) {
      newErrors.phone_number = "Número de teléfono inválido. Debe tener 9 dígitos.";
    }

    if (formData.email && !emailRegex.test(formData.email)) {
      newErrors.email = "Correo electrónico inválido.";
    }

    if (formData.founded_date && !dateRegex.test(formData.founded_date)) {
      newErrors.founded_date = "Fecha de fundación inválida. Debe ser en formato YYYY-MM-DD.";
    }
    if (formData.address && formData.address.length > 100) {
      newErrors.address = "La dirección no puede superar los 200 caracteres.";
    }
    if (formData.name && formData.name.length > 40) {
      newErrors.name = "El nombre no puede superar los 40 caracteres.";
    }
    if (formData.industry && formData.industry.length > 50) {
      newErrors.industry = "El sector industrial no puede superar los 50 caracteres.";
    }

    if (formData.country && formData.country.length > 30) {
      newErrors.country = "El país no puede superar los 30 caracteres.";
    }

    if (formData.tax_id && formData.tax_id.length > 15) {
      newErrors.tax_id = "El ID fiscal no puede superar los 15 caracteres.";
    }
    setErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      alert("Por favor, corrija los errores antes de guardar.");
      return;
    }

    try {
      const token = localStorage.getItem("token");
      await axios.put(`${process.env.REACT_APP_API_URL}/companies/profile`, formData, {
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
      <MDBox
        mb={2}
        sx={{
          display: "flex",
          flexDirection: "column",
          flexGrow: 1,
          minHeight: "calc(100vh - 64px)",
        }}
      >
        {/* Header */}
        <Card
          sx={{
            p: 3,
            backgroundColor: "background.paper", // Se adapta al fondo automáticamente
            boxShadow: "none",
          }}
        >
          <MDBox>
            <MDTypography
              variant="h4"
              fontWeight="bold"
              sx={{
                color: "text.primary", // Se adapta automáticamente
                fontSize: "2rem",
                marginBottom: 1,
              }}
            >
              {company.name}
            </MDTypography>
            <MDTypography
              variant="h6"
              fontWeight="regular"
              sx={{
                color: "text.secondary", // Se adapta automáticamente
                fontSize: "1.25rem",
              }}
            >
              {company.industry || "Industria no especificada"}
            </MDTypography>
          </MDBox>
        </Card>

        {/* Content */}
        <Grid container spacing={3} mt={2}>
          <Grid item xs={12} md={6} xl={4}>
            <PlatformSettings />
          </Grid>

          <Grid item xs={12} md={6} xl={4}>
            <Card sx={{ boxShadow: "none" }}>
              <MDBox p={2}>
                <MDTypography variant="h6" fontWeight="medium" textTransform="capitalize">
                  Información de la Empresa
                </MDTypography>
              </MDBox>
              <MDBox pt={1} pb={2} px={2} lineHeight={1.25}>
                <MDBox display="flex" justifyContent="space-between" alignItems="center" mb={2}>
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
                    "country",
                    "tax_id",
                    "founded_date",
                  ].map((field) => (
                    <Grid item xs={12} sm={6} key={field}>
                      <MDTypography
                        variant="caption"
                        fontWeight="bold"
                        color="text"
                        textTransform="uppercase"
                      >
                        {field.replace("_", " ").toUpperCase()}
                      </MDTypography>
                      {isEditing ? (
                        <>
                          {field === "founded_date" ? (
                            <>
                              <input
                                type="date"
                                name={field}
                                value={formData[field] || ""}
                                onChange={handleChange}
                                className="MuiInputBase-input MuiInput-input MuiInputBase-inputAdornedEnd"
                                style={{
                                  width: "100%",
                                  padding: "8px",
                                  border: "1px solid #ccc",
                                  borderRadius: "4px",
                                }}
                              />
                              {errors[field] && (
                                <MDTypography variant="caption" color="error">
                                  {errors[field]}
                                </MDTypography>
                              )}
                            </>
                          ) : (
                            <MDInput
                              fullWidth
                              name={field}
                              value={formData[field] || ""}
                              onChange={handleChange}
                              error={Boolean(errors[field])}
                              helperText={errors[field]}
                            />
                          )}
                        </>
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
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default CompanyProfile;
