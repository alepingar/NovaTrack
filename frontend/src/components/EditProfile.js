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
        logo_url: "",
    });
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
                    logo_url: data.logo_url || "",
                });
            } catch (error) {
                console.error("Error al obtener los datos de la empresa:", error);
            }
        };

        fetchCompanyData();
    }, []);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
    
        // Reemplaza valores vacíos con null para campos opcionales
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
                        <div className="mb-3">
                            <label htmlFor="name" className="form-label">Nombre de la Empresa</label>
                            <input
                                type="text"
                                className="form-control"
                                id="name"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className="mb-3">
                            <label htmlFor="email" className="form-label">Correo Electrónico</label>
                            <input
                                type="email"
                                className="form-control"
                                id="email"
                                name="email"
                                value={formData.email}
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
                                value={formData.industry}
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
                                value={formData.address}
                                onChange={handleChange}
                            />
                        </div>
                        <div className="mb-3">
                            <label htmlFor="phone_number" className="form-label">Teléfono</label>
                            <input
                                type="text"
                                className="form-control"
                                id="phone_number"
                                name="phone_number"
                                value={formData.phone_number}
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
                                value={formData.website}
                                onChange={handleChange}
                            />
                        </div>
                        <div className="mb-3">
                            <label htmlFor="country" className="form-label">País</label>
                            <input
                                type="text"
                                className="form-control"
                                id="country"
                                name="country"
                                value={formData.country}
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
                                value={formData.tax_id}
                                onChange={handleChange}
                            />
                        </div>
                        <div className="mb-3">
                            <label htmlFor="description" className="form-label">Descripción</label>
                            <textarea
                                className="form-control"
                                id="description"
                                name="description"
                                rows="3"
                                value={formData.description}
                                onChange={handleChange}
                            ></textarea>
                        </div>
                        <div className="mb-3">
                            <label htmlFor="founded_date" className="form-label">Fecha de Fundación</label>
                            <input
                                type="date"
                                className="form-control"
                                id="founded_date"
                                name="founded_date"
                                value={formData.founded_date}
                                onChange={handleChange}
                            />
                        </div>
                        <div className="mb-3">
                            <label htmlFor="logo_url" className="form-label">URL del Logo</label>
                            <input
                                type="url"
                                className="form-control"
                                id="logo_url"
                                name="logo_url"
                                value={formData.logo_url}
                                onChange={handleChange}
                            />
                        </div>
                        <button type="submit" className="btn btn-primary w-100">Guardar Cambios</button>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default EditProfile;
