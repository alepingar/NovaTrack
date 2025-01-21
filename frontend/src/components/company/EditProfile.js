import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function EditProfile() {
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        industry: "",
        address: "",
        phone_number: "",
        website: "",
        country: "",
        tax_id: "",
        description: "",
        founded_date: "",
    });

    const [errors, setErrors] = useState({});
    const navigate = useNavigate();

    useEffect(() => {
        const fetchCompanyData = async () => {
            try {
                const token = localStorage.getItem("token");
                const response = await axios.get("http://127.0.0.1:8000/companies/profile", {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                const data = response.data;
                setFormData({
                    name: data.name,
                    email: data.email,
                    industry: data.industry || "",
                    address: data.address || "",
                    phone_number: data.phone_number || "",
                    website: data.website || "",
                    country: data.country || "",
                    tax_id: data.tax_id || "",
                    description: data.description || "",
                    founded_date: data.founded_date ? new Date(data.founded_date).toISOString().slice(0, 10) : "",
                });
            } catch (error) {
                console.error("Error al obtener los datos de la empresa:", error);
            }
        };

        fetchCompanyData();
    }, []);

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

        const sanitizedData = Object.fromEntries(
            Object.entries(formData).map(([key, value]) => [key, value.trim() === "" ? null : value])
        );

        try {
            const token = localStorage.getItem("token");
            await axios.put("http://127.0.0.1:8000/companies/profile", sanitizedData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            alert("Perfil actualizado correctamente");
            navigate("/profile");
        } catch (error) {
            alert("Error al actualizar el perfil");
            console.error("Error:", error.response?.data || error.message);
        }
    };

    return (
        <div className="container mt-5">
            <div className="card shadow">
                <div className="card-header bg-primary text-white">
                    <h3>Editar Perfil</h3>
                </div>
                <div className="card-body">
                    <form onSubmit={handleSubmit}>
                        {[
                            { id: "name", label: "Nombre de la Empresa", required: true },
                            { id: "email", label: "Correo Electrónico", required: true },
                            { id: "industry", label: "Industria" },
                            { id: "address", label: "Dirección" },
                            { id: "phone_number", label: "Teléfono" },
                            { id: "website", label: "Sitio Web", type: "url" },
                            { id: "country", label: "País", required: true },
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
                        <button type="submit" className="btn btn-primary w-100">Guardar Cambios</button>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default EditProfile;
