import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";

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

    const [errors, setErrors] = useState({});
    const [errorMessage, setErrorMessage] = useState(null);
    const navigate = useNavigate();

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
            setErrorMessage(null); // Reinicia el mensaje de error

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
            if (error.response && error.response.data) {
                const details = error.response.data.detail;
                if (Array.isArray(details)) {
                    setErrorMessage(details.map((d) => `${d.loc?.join(".")}: ${d.msg}`).join(", "));
                } else {
                    setErrorMessage(details || "Error al registrar la empresa");
                }
            } else {
                setErrorMessage("No se pudo conectar con el servidor.");
            }
        }
    };

    return (
        <div className="container mt-5">
            <div className="row justify-content-center">
                <div className="col-md-8">
                    <div className="card shadow">
                        <div className="card-header text-center">
                            <h2>Registro de Empresa</h2>
                        </div>
                        <div className="card-body">
                            {errorMessage && (
                                <div className="alert alert-danger text-center">
                                    {errorMessage}
                                </div>
                            )}
                            <form onSubmit={handleSubmit}>
                                {[
                                    { id: "name", label: "Nombre de la Empresa", required: true },
                                    { id: "email", label: "Correo Electrónico", required: true },
                                    { id: "password", label: "Contraseña", required: true, type: "password" },
                                    { id: "confirm_password", label: "Confirmar Contraseña", required: true, type: "password" },
                                    { id: "country", label: "País", required: true },
                                    { id: "industry", label: "Industria" },
                                    { id: "address", label: "Dirección" },
                                    { id: "phone_number", label: "Teléfono" },
                                    { id: "website", label: "Sitio Web", type: "url" },
                                    { id: "tax_id", label: "ID Fiscal" },
                                    { id: "description", label: "Descripción", type: "textarea" },
                                    { id: "founded_date", label: "Fecha de Fundación", type: "date" },
                                ].map(({ id, label, required, type = "text" }) => (
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
                                <button type="submit" className="btn btn-primary w-100">Registrar</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default RegisterCompany;
