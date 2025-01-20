import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import "../css/RegisterCompany.css";

function RegisterCompany() {
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
        if (currentStep < steps.length - 1) setCurrentStep(currentStep + 1);
    };

    const prevStep = () => {
        if (currentStep > 0) setCurrentStep(currentStep - 1);
    };

    return (
        <div className="d-flex" style={{ height: "100vh" }}>
            <div className="col-md-6 d-flex align-items-center justify-content-center bg-dark text-white text-center">
                <div>
                    <h1 className="mb-4">Crea tu cuenta empresarial</h1>
                    <p>Explora funciones avanzadas y optimiza tus operaciones.</p>
                </div>
            </div>
            <div className="col-md-6 d-flex align-items-center">
                <div className="container">
                    <div className="card shadow">
                        <div className="card-header bg-primary text-white text-center">
                            <h2>{steps[currentStep].title}</h2>
                        </div>
                        <div className="card-body">
                            {errorMessage && (
                                <div className="alert alert-danger text-center">
                                    {errorMessage}
                                </div>
                            )}
                            <form onSubmit={handleSubmit}>
                                {steps[currentStep].fields.map(({ id, label, required, type = "text" }) => (
                                    <div className="mb-3" key={id}>
                                        <label htmlFor={id} className="form-label">
                                            {label} {required && <span className="text-danger">*</span>}
                                        </label>
                                        {type === "textarea" ? (
                                            <textarea
                                                className={`form-control ${errors[id] ? "is-invalid" : ""}`}
                                                id={id}
                                                name={id}
                                                placeholder={label}
                                                value={formData[id]}
                                                onChange={handleChange}
                                            />
                                        ) : (
                                            <input
                                                type={type}
                                                className={`form-control ${errors[id] ? "is-invalid" : ""}`}
                                                id={id}
                                                name={id}
                                                placeholder={label}
                                                value={formData[id]}
                                                onChange={handleChange}
                                            />
                                        )}
                                        {errors[id] && <div className="invalid-feedback">{errors[id]}</div>}
                                    </div>
                                ))}
                                <div className="d-flex justify-content-between">
                                    {currentStep > 0 && (
                                        <button type="button" className="btn btn-secondary" onClick={prevStep}>
                                            Atrás
                                        </button>
                                    )}
                                    {currentStep < steps.length - 1 ? (
                                        <button type="button" className="btn btn-primary" onClick={nextStep}>
                                            Siguiente
                                        </button>
                                    ) : (
                                        <button type="submit" className="btn btn-success">
                                            Registrar
                                        </button>
                                    )}
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default RegisterCompany;
