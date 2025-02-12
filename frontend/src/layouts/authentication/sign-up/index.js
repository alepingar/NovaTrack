import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Card from "@mui/material/Card";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";
import CoverLayout from "layouts/authentication/components/CoverLayout";

function Cover() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirm_password: "",
    country: "",
    industry: "",
    address: "",
    phone_number: "",
    website: "",
    tax_id: "",
    description: "",
    founded_date: "",
  });

  const [currentStep, setCurrentStep] = useState(0);
  const [errors, setErrors] = useState({});
  const [errorMessage, setErrorMessage] = useState(null);
  const navigate = useNavigate();

  const steps = [
    {
      title: "Información Básica",
      fields: [
        { id: "name", label: "Nombre de la Empresa", required: true },
        { id: "email", label: "Correo Electrónico", required: true },
        { id: "password", label: "Contraseña", required: true, type: "password" },
        { id: "confirm_password", label: "Confirmar Contraseña", required: true, type: "password" },
      ],
    },
    {
      title: "Detalles de Contacto",
      fields: [
        { id: "country", label: "País", required: true },
        { id: "phone_number", label: "Teléfono" },
        { id: "address", label: "Dirección" },
        { id: "website", label: "Sitio Web", type: "url" },
      ],
    },
    {
      title: "Información Adicional",
      fields: [
        { id: "industry", label: "Industria" },
        { id: "tax_id", label: "ID Fiscal" },
        { id: "description", label: "Descripción", type: "textarea" },
        { id: "founded_date", label: "Fecha de Fundación", type: "date" },
      ],
    },
  ];

  const validateField = (name, value) => {
    let error = "";
    switch (name) {
      case "name":
        if (value.trim().length < 2 || value.trim().length > 40) {
          error = "El nombre debe tener entre 2 y 40 caracteres.";
        }
        break;
      case "email":
        if (!/^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/.test(value)) {
          error = "Introduce un correo electrónico válido.";
        }
        break;
      case "password":
        if (value.trim().length < 8 || value.trim().length > 50) {
          error = "La contraseña debe tener entre 8 y 50 caracteres.";
        }
        break;
      case "confirm_password":
        if (value !== formData.password) {
          error = "Las contraseñas no coinciden.";
        }
        break;
      case "phone_number":
        if (value && !/^\+?[1-9]\d{1,14}$/.test(value)) {
          error = "El número de teléfono debe seguir el formato internacional (E.164).";
        }
        break;
      case "tax_id":
        if (value.trim().length < 8 || value.trim().length > 15) {
          error = "El ID fiscal debe tener entre 8 y 15 caracteres.";
        }
        break;
      case "website":
        if (value && !/^https?:\/\/[\w\-]+(\.[\w\-]+)+[/#?]?.*$/.test(value)) {
          error = "Introduce una URL válida.";
        }
        break;
      case "country":
        if (value.trim().length < 2 || value.trim().length > 50) {
          error = "El país debe tener entre 2 y 50 caracteres.";
        }
        break;
      default:
        break;
    }
    return error;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    const error = validateField(name, value);
    setErrors((prevErrors) => ({
      ...prevErrors,
      [name]: error,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = {};
    Object.keys(formData).forEach((key) => {
      const error = validateField(key, formData[key]);
      if (error) {
        newErrors[key] = error;
      }
    });

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      setErrorMessage(null);
      const payload = Object.fromEntries(
        Object.entries(formData).filter(([_, value]) => value.trim() !== "")
      );
      if (payload.founded_date) {
        payload.founded_date = new Date(payload.founded_date).toISOString();
      }
      await axios.post("http://127.0.0.1:8000/companies/register", payload);
      alert("Registro exitoso");
      navigate("/login");
    } catch (error) {
      console.error("Error del servidor:", error.response?.data || error.message);
      setErrorMessage("No se pudo conectar con el servidor.");
    }
  };

  const nextStep = () => {
    const currentFields = steps[currentStep].fields;
    const invalidFields = currentFields.some((field) => {
      return !formData[field.id] || errors[field.id];
    });
    if (!invalidFields) {
      if (currentStep < steps.length - 1) setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) setCurrentStep(currentStep - 1);
  };

  return (
    <Grid container style={{ backgroundColor: "#2c3e50" }}>
      <CoverLayout>
        <Card>
          <MDBox
            variant="gradient"
            bgColor="dark"
            borderRadius="lg"
            coloredShadow="success"
            mx={2}
            mt={-3}
            p={3}
            mb={1}
            textAlign="center"
          >
            <MDTypography variant="h4" fontWeight="medium" color="white" mt={1}>
              {steps[currentStep].title}
            </MDTypography>
            <MDTypography display="block" variant="button" color="white" my={1}>
              Completa la información para continuar
            </MDTypography>
          </MDBox>
          <MDBox pt={4} pb={3} px={3}>
            {errorMessage && (
              <MDBox mb={2}>
                <MDTypography variant="button" color="error" textAlign="center">
                  {errorMessage}
                </MDTypography>
              </MDBox>
            )}
            <MDBox component="form" role="form" onSubmit={handleSubmit}>
              {steps[currentStep].fields.map(({ id, label, required, type = "text" }) => (
                <MDBox mb={2} key={id}>
                  {type === "textarea" ? (
                    <MDInput
                      multiline
                      rows={4}
                      variant="standard"
                      fullWidth
                      id={id}
                      name={id}
                      label={label}
                      required={required}
                      value={formData[id]}
                      onChange={handleChange}
                      error={Boolean(errors[id])}
                      helperText={errors[id]}
                    />
                  ) : (
                    <MDInput
                      type={type}
                      variant="standard"
                      fullWidth
                      id={id}
                      name={id}
                      label={label}
                      required={required}
                      value={formData[id]}
                      onChange={handleChange}
                      error={Boolean(errors[id])}
                      helperText={errors[id]}
                    />
                  )}
                </MDBox>
              ))}
              <MDBox mt={4} mb={1} display="flex" justifyContent="space-between">
                {currentStep > 0 && (
                  <MDButton variant="outlined" color="dark" onClick={prevStep}>
                    Atrás
                  </MDButton>
                )}
                {currentStep < steps.length - 1 ? (
                  <MDButton variant="gradient" color="dark" onClick={nextStep}>
                    Siguiente
                  </MDButton>
                ) : (
                  <MDButton variant="gradient" color="success" type="submit">
                    Registrar
                  </MDButton>
                )}
              </MDBox>
            </MDBox>
          </MDBox>
        </Card>
      </CoverLayout>
    </Grid>
  );
}
export default Cover;
