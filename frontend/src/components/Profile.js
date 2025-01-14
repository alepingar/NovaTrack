import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function Profile() {
    const [company, setCompany] = useState(null);

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
                setCompany(response.data);
            } catch (error) {
                console.error("Error al obtener los datos de la empresa:", error);
            }
        };

        fetchCompanyData();
    }, []);

    if (!company) {
        return (
            <div className="container mt-4">
                <p className="text-center text-secondary">Cargando información...</p>
            </div>
        );
    }

    return (
        <div className="container mt-5">
            <div className="card shadow">
                <div className="card-header bg-primary text-white">
                    <h3>Perfil de la Empresa</h3>
                </div>
                <div className="card-body">
                    <p className="text-dark"><strong>Nombre:</strong> {company.name}</p>
                    <p className="text-dark"><strong>Email:</strong> {company.email}</p>
                    <p className="text-dark"><strong>Industria:</strong> {company.industry || "No especificada"}</p>
                </div>
                <button
                    className="dropdown-item"
                    onClick={() => navigate("/edit-profile")}
                >
                Editar Perfil
                </button>
            </div>
        </div>
    );
}

export default Profile;
