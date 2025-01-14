import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function EditProfile() {
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        industry: ""
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
                setFormData({
                    name: response.data.name,
                    email: response.data.email,
                    industry: response.data.industry || "",
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
        try {
            const token = localStorage.getItem("token");
            await axios.put("http://127.0.0.1:8000/companies/profile", formData, {
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
                        <button type="submit" className="btn btn-primary w-100">Guardar Cambios</button>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default EditProfile;
