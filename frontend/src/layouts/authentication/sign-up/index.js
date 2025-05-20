import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Card from "@mui/material/Card";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import CoverLayout from "layouts/authentication/components/CoverLayout";
import {
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  IconButton,
  InputAdornment,
} from "@mui/material";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import TermsModal from "./components/termsModal";
import PrivacyModal from "./components/privacyModal";
import DataProcessingModal from "./components/dataProcessingModal";

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
    tax_id: "",
    founded_date: "",
    billing_account_number: "",
    entity_type: "",
    terms_accepted: false,
    privacy_policy_accepted: false,
    data_processing_consent: false,
  });

  const [currentStep, setCurrentStep] = useState(() => {
    return parseInt(localStorage.getItem("currentStep")) || 0;
  });
  const [errors, setErrors] = useState({});
  const [errorMessage, setErrorMessage] = useState(null);
  const [entityTypes, setEntityTypes] = useState([]);
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [openTermsModal, setOpenTermsModal] = useState(false);
  const [openPrivacyModal, setOpenPrivacyModal] = useState(false);
  const [openDataProcessingModal, setOpenDataProcessingModal] = useState(false);

  const handleOpenTermsModal = () => setOpenTermsModal(true);
  const handleCloseTermsModal = () => setOpenTermsModal(false);

  const handleOpenPrivacyModal = () => setOpenPrivacyModal(true);
  const handleClosePrivacyModal = () => setOpenPrivacyModal(false);

  const handleOpenDataProcessingModal = () => setOpenDataProcessingModal(true);
  const handleCloseDataProcessingModal = () => setOpenDataProcessingModal(false);

  const [formSubmitted, setFormSubmitted] = useState(false);

  useEffect(() => {
    const fetchEntityTypes = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/companies/get-types`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setEntityTypes(response.data);
      } catch (error) {
        console.error("Error al obtener los tipos de entidad:", error);
      }
    };
    fetchEntityTypes();
  }, []);

  useEffect(() => {
    localStorage.setItem("currentStep", currentStep);
  }, [currentStep]);

  useEffect(() => {
    const storedFormData = JSON.parse(localStorage.getItem("formData"));
    if (storedFormData) {
      setFormData(storedFormData);
    }
  }, []);
  useEffect(() => {
    localStorage.setItem("formData", JSON.stringify(formData));
  }, [formData]);

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
      ],
    },
    {
      title: "Información Adicional",
      fields: [
        { id: "industry", label: "Industria" },
        { id: "tax_id", label: "ID Fiscal" },
        { id: "founded_date", label: "Fecha de Fundación", type: "date" },
      ],
    },
    {
      title: "Información Fiscal y Términos",
      fields: [
        { id: "billing_account_number", label: "Número de Cuenta de Facturación", required: true },
        {
          id: "entity_type",
          label: "Tipo de Entidad",
          required: true,
          type: "select",
        },
      ],
    },
    {
      title: "Aceptación de Términos y Políticas",
      fields: [],
    },
  ];

  const validateField = async (name, value) => {
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
        } else if (value) {
          try {
            const response = await axios.get(
              `${process.env.REACT_APP_API_URL}/auth/check-email/${value}`
            );
            if (response.data.exists) {
              error = "Este correo electrónico ya está en uso.";
            }
          } catch (serverError) {
            error = "El servidor no pudo validar el correo electrónico.";
          }
        }
        break;
      case "password":
        if (value.trim().length < 8 || value.trim().length > 50) {
          error = "La contraseña debe tener entre 8 y 50 caracteres.";
        }
        break;
      case "founded_date":
        const foundedDate = new Date(value);
        const currentDate = new Date();
        if (foundedDate > currentDate) {
          error = "La fecha de fundación no puede ser futura.";
        } else if (foundedDate.getFullYear() < 1800) {
          error = "La fecha de fundación no puede ser anterior a 1800.";
        }
        break;
      case "industry":
        if (value.trim().length > 50) {
          error = "La industria debe de tener menos de 50 carácteres de longitud.";
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
      case "address":
        if (value.trim().length > 100) {
          error = "La dirección debe tener menos de 100 caracteres.";
        }
        break;
      case "tax_id":
        if (value.trim().length > 15) {
          error = "El ID fiscal debe tener entre 8 y 15 caracteres.";
        }
        break;
      case "country":
        if (value.trim().length < 2 || value.trim().length > 50) {
          error = "El país debe tener entre 2 y 50 caracteres.";
        }
        break;
      case "billing_account_number":
        if (value && !/^ES\d{2}\d{20}$/.test(value)) {
          error = "El número de cuenta debe ser un IBAN español válido, formado por 24 dígitos.";
        }
        break;
      default:
        break;
    }
    return error;
  };

  const handleChange = async (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    const error = await validateField(name, value);
    setErrors((prevErrors) => ({
      ...prevErrors,
      [name]: error,
    }));
  };

  const handleCheckboxChange = (e) => {
    const { name, checked } = e.target;
    setFormData((prev) => ({ ...prev, [name]: checked }));
    setErrors((prevErrors) => ({
      ...prevErrors,
      [name]: checked ? "" : prevErrors[name],
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormSubmitted(true);

    const newErrors = {};

    Object.keys(formData).forEach((key) => {
      if (steps[currentStep].fields.some((field) => field.id === key && field.required)) {
        const error = validateField(key, formData[key]);
        if (error) {
          newErrors[key] = error;
        }
      }
    });

    if (!formData.terms_accepted) {
      newErrors.terms_accepted = "Debes aceptar los términos y condiciones.";
    }
    if (!formData.privacy_policy_accepted) {
      newErrors.privacy_policy_accepted = "Debes aceptar la política de privacidad.";
    }
    if (!formData.data_processing_consent) {
      newErrors.data_processing_consent = "Debes aceptar el procesamiento de datos.";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    const payload = { ...formData };
    Object.keys(payload).forEach((key) => {
      if (payload[key] === "") {
        payload[key] = null;
      }
    });

    try {
      setErrorMessage(null);
      if (payload.founded_date) {
        payload.founded_date = new Date(payload.founded_date).toISOString();
      }
      await axios.post(`${process.env.REACT_APP_API_URL}/companies/register`, payload);
      alert("Registro exitoso");
      localStorage.removeItem("currentStep");
      localStorage.removeItem("formData");
      navigate("/authentication/sign-in");
    } catch (error) {
      console.error("Error del servidor:", error.response?.data || error.message);
    }
  };

  const nextStep = () => {
    const currentFields = steps[currentStep].fields;
    const invalidFields = currentFields.some((field) => {
      if (field.required) {
        return !formData[field.id] || errors[field.id];
      }
      return errors[field.id];
    });
    if (!invalidFields && currentStep < steps.length - 1) {
      setCurrentStep((prevStep) => {
        const newStep = prevStep + 1;
        localStorage.setItem("currentStep", newStep);
        return newStep;
      });
    }
  };
  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep((prevStep) => {
        const newStep = prevStep - 1;
        localStorage.setItem("currentStep", newStep);
        return newStep;
      });
    }
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
                  {type === "password" ? (
                    <MDInput
                      variant="standard"
                      fullWidth
                      id={id}
                      label={label}
                      required={required}
                      value={formData[id]}
                      onChange={handleChange}
                      name={id}
                      error={Boolean(errors[id])}
                      helperText={errors[id]}
                      type={
                        id === "password"
                          ? showPassword
                            ? "text"
                            : "password"
                          : showConfirmPassword
                          ? "text"
                          : "password"
                      }
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              aria-label="toggle password visibility"
                              onClick={() => {
                                if (id === "password") {
                                  setShowPassword(!showPassword);
                                } else {
                                  setShowConfirmPassword(!showConfirmPassword);
                                }
                              }}
                              edge="end"
                            >
                              {id === "password" ? (
                                showPassword ? (
                                  <VisibilityOff />
                                ) : (
                                  <Visibility />
                                )
                              ) : showConfirmPassword ? (
                                <VisibilityOff />
                              ) : (
                                <Visibility />
                              )}
                            </IconButton>
                          </InputAdornment>
                        ),
                      }}
                    />
                  ) : type === "select" ? (
                    <FormControl
                      fullWidth
                      error={Boolean(errors[id])}
                      sx={{ marginTop: 1, marginBottom: 2 }}
                    >
                      <InputLabel required={required}>{label}</InputLabel>{" "}
                      <Select
                        value={formData[id]}
                        onChange={handleChange}
                        label={label}
                        name={id}
                        required={required}
                      >
                        {entityTypes.map((typeValue) => (
                          <MenuItem key={typeValue} value={typeValue}>
                            {typeValue}
                          </MenuItem>
                        ))}
                      </Select>
                      {errors[id] && (
                        <MDTypography variant="button" color="error">
                          {errors[id]}
                        </MDTypography>
                      )}
                    </FormControl>
                  ) : type === "textarea" ? (
                    <MDInput
                      multiline
                      rows={4}
                      variant="standard"
                      fullWidth
                      id={id}
                      label={label}
                      required={required}
                      value={formData[id]}
                      onChange={handleChange}
                      name={id}
                      error={Boolean(errors[id])}
                      helperText={errors[id]}
                    />
                  ) : (
                    <MDInput
                      variant="standard"
                      fullWidth
                      id={id}
                      label={label}
                      required={required}
                      value={formData[id]}
                      onChange={handleChange}
                      name={id}
                      error={Boolean(errors[id])}
                      helperText={errors[id]}
                      type={type}
                    />
                  )}
                </MDBox>
              ))}
              {currentStep === steps.length - 1 && (
                <>
                  <MDBox mb={2}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={formData.terms_accepted}
                          onChange={handleCheckboxChange}
                          name="terms_accepted"
                        />
                      }
                      label={
                        <span>
                          Acepto los{" "}
                          <a
                            href="#"
                            onClick={(e) => {
                              e.preventDefault();
                              handleOpenTermsModal();
                            }}
                          >
                            términos y condiciones de uso
                          </a>
                        </span>
                      }
                    />
                    {formSubmitted && errors.terms_accepted && (
                      <MDTypography color="error">{errors.terms_accepted}</MDTypography>
                    )}
                  </MDBox>
                  <MDBox mb={2}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={formData.privacy_policy_accepted}
                          onChange={handleCheckboxChange}
                          name="privacy_policy_accepted"
                        />
                      }
                      label={
                        <span>
                          Acepto la{" "}
                          <a
                            href="#"
                            onClick={(e) => {
                              e.preventDefault();
                              handleOpenPrivacyModal(); // Corrección: Invoca la función
                            }}
                          >
                            política de privacidad
                          </a>
                        </span>
                      }
                    />
                    {formSubmitted && errors.privacy_policy_accepted && (
                      <MDTypography color="error">{errors.privacy_policy_accepted}</MDTypography>
                    )}
                  </MDBox>
                  <MDBox mb={2}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={formData.data_processing_consent}
                          onChange={handleCheckboxChange}
                          name="data_processing_consent"
                        />
                      }
                      label={
                        <span>
                          Acepto el{" "}
                          <a
                            href="#"
                            onClick={(e) => {
                              e.preventDefault();
                              handleOpenDataProcessingModal(); // Corrección: Invoca la función
                            }}
                          >
                            procesamiento de mis datos
                          </a>
                        </span>
                      }
                    />
                    {formSubmitted && errors.data_processing_consent && (
                      <MDTypography color="error">{errors.data_processing_consent}</MDTypography>
                    )}
                  </MDBox>
                </>
              )}
              <MDBox display="flex" justifyContent="space-between">
                {currentStep > 0 && (
                  <MDButton variant="outlined" color="secondary" onClick={prevStep}>
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
      <TermsModal open={openTermsModal} onClose={handleCloseTermsModal} />
      <PrivacyModal open={openPrivacyModal} onClose={handleClosePrivacyModal} />
      <DataProcessingModal
        open={openDataProcessingModal}
        onClose={handleCloseDataProcessingModal}
      />
    </Grid>
  );
}

export default Cover;
