import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";

function RegisterCompany() {
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        password: "",
        country: "",
        industry: "",
        address: "",
        phone_number: "",
        website: "",
        tax_id: "",
        description: "",
        founded_date: "",
        logo_url: "",
    });

    const [errorMessage, setErrorMessage] = useState(null);
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            setErrorMessage(null); // Reinicia el mensaje de error
    
            // Filtra campos vacíos
            const payload = Object.fromEntries(
                Object.entries(formData).filter(([_, value]) => value.trim() !== "")
            );
    
            // Convierte la fecha si está definida
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
                    setErrorMessage(details.map(d => `${d.loc?.join(".")}: ${d.msg}`).join(", "));
                } else {
                    setErrorMessage(details || "Error al registrar la empresa");
                }
            } else {
                setErrorMessage("No se pudo conectar con el servidor.");
            }
        }
    };

    const handleImageUpload = async (file) => {
        const formData = new FormData();
        formData.append("file", file);
    
        try {
            const token = localStorage.getItem("token");
            const response = await axios.post("http://127.0.0.1:8000/upload/logo", formData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "multipart/form-data",
                },
            });
            alert("Imagen subida correctamente");
            // Actualiza el estado o recarga los datos
        } catch (error) {
            console.error("Error al subir la imagen:", error);
            alert("Error al subir la imagen");
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
                                <div className="mb-3">
                                    <label htmlFor="name" className="form-label">
                                        Nombre de la Empresa <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        id="name"
                                        name="name"
                                        placeholder="Nombre de la Empresa"
                                        onChange={handleChange}
                                        required
                                    />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="email" className="form-label">
                                        Correo Electrónico <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="email"
                                        className="form-control"
                                        id="email"
                                        name="email"
                                        placeholder="Correo Electrónico"
                                        onChange={handleChange}
                                        required
                                    />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="password" className="form-label">
                                        Contraseña <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="password"
                                        className="form-control"
                                        id="password"
                                        name="password"
                                        placeholder="Contraseña"
                                        onChange={handleChange}
                                        required
                                    />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="country" className="form-label">
                                        País <span className="text-danger">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        id="country"
                                        name="country"
                                        placeholder="País de la Empresa"
                                        onChange={handleChange}
                                        required
                                    />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="industry" className="form-label">Industria</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        id="industry"
                                        name="industry"
                                        placeholder="Industria"
                                        onChange={handleChange}
                                    />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="address" className="form-label">Dirección</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        id="address"
                                        name="address"
                                        placeholder="Dirección de la Empresa"
                                        onChange={handleChange}
                                    />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="phone_number" className="form-label">Teléfono</label>
                                    <input
                                        type="tel"
                                        className="form-control"
                                        id="phone_number"
                                        name="phone_number"
                                        placeholder="Teléfono de la Empresa"
                                        onChange={handleChange}
                                    />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="website" className="form-label">Sitio Web</label>
                                    <input
                                        type="url"
                                        className="form-control"
                                        id="website"
                                        name="website"
                                        placeholder="URL del Sitio Web"
                                        onChange={handleChange}
                                    />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="tax_id" className="form-label">ID Fiscal</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        id="tax_id"
                                        name="tax_id"
                                        placeholder="ID Fiscal de la Empresa"
                                        onChange={handleChange}
                                    />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="description" className="form-label">Descripción</label>
                                    <textarea
                                        className="form-control"
                                        id="description"
                                        name="description"
                                        placeholder="Breve descripción de la empresa"
                                        onChange={handleChange}
                                        rows="4"
                                    />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="founded_date" className="form-label">Fecha de Fundación</label>
                                    <input
                                        type="date"
                                        className="form-control"
                                        id="founded_date"
                                        name="founded_date"
                                        onChange={handleChange}
                                    />
                                </div>
                                <div className="mb-3">
                                    <label htmlFor="profileImage" className="form-label">Imagen de Perfil</label>
                                    <input
                                        type="file"
                                        className="form-control"
                                        id="profileImage"
                                        onChange={(e) => handleImageUpload(e.target.files[0])}
                                    />
                                </div>
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
