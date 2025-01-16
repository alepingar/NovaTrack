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
                    <p className="text-dark"><strong>Dirección:</strong> {company.address || "No especificada"}</p>
                    <p className="text-dark"><strong>Teléfono:</strong> {company.phone_number || "No especificado"}</p>
                    <p className="text-dark"><strong>Sitio Web:</strong> {company.website || "No especificado"}</p>
                    <p className="text-dark"><strong>ID Fiscal:</strong> {company.tax_id || "No especificado"}</p>
                    <p className="text-dark"><strong>Descripción:</strong> {company.description || "No especificada"}</p>
                    <p className="text-dark"><strong>País:</strong> {company.country || "No especificado"}</p>
                    <p className="text-dark"><strong>Fecha de Fundación:</strong> {company.founded_date ? new Date(company.founded_date).toLocaleDateString() : "No especificada"}</p>
                    <p className="text-dark"><strong>Logo:</strong> {company.logo_url ? <a href={company.logo_url} target="_blank" rel="noopener noreferrer">Ver Logo</a> : "No especificado"}</p>
                    <p className="text-dark"><strong>Fecha de Creación:</strong> {new Date(company.created_at).toLocaleDateString()}</p>
                    <p className="text-dark"><strong>Última Actualización:</strong> {new Date(company.updated_at).toLocaleDateString()}</p>
                </div>
                <div className="card-footer text-end">
                    <button
                        className="btn btn-primary"
                        onClick={() => navigate("/edit-profile")}
                    >
                        Editar Perfil
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Profile;
