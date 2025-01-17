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
            <div className="container mt-5 text-center">
                <p className="text-secondary">Cargando información...</p>
            </div>
        );
    }

    return (
        <div className="container mt-5">
            <div className="card shadow-lg border-0">
                <div className="card-header bg-dark text-white">
                    <h3 className="mb-0">Perfil de la Empresa</h3>
                </div>
                <div className="card-body">
                    <div className="row mb-3">
                        <div className="col-md-6">
                            <p className="mb-1 text-muted">Nombre</p>
                            <h5>{company.name}</h5>
                        </div>
                        <div className="col-md-6">
                            <p className="mb-1 text-muted">Email</p>
                            <h5>{company.email}</h5>
                        </div>
                    </div>
                    <div className="row mb-3">
                        <div className="col-md-6">
                            <p className="mb-1 text-muted">Industria</p>
                            <h5>{company.industry || "No especificada"}</h5>
                        </div>
                        <div className="col-md-6">
                            <p className="mb-1 text-muted">Dirección</p>
                            <h5>{company.address || "No especificada"}</h5>
                        </div>
                    </div>
                    <div className="row mb-3">
                        <div className="col-md-6">
                            <p className="mb-1 text-muted">Teléfono</p>
                            <h5>{company.phone_number || "No especificado"}</h5>
                        </div>
                        <div className="col-md-6">
                            <p className="mb-1 text-muted">Sitio Web</p>
                            <h5>
                                {company.website ? (
                                    <a href={company.website} target="_blank" rel="noopener noreferrer">
                                        {company.website}
                                    </a>
                                ) : (
                                    "No especificado"
                                )}
                            </h5>
                        </div>
                    </div>
                    <div className="row mb-3">
                        <div className="col-md-6">
                            <p className="mb-1 text-muted">ID Fiscal</p>
                            <h5>{company.tax_id || "No especificado"}</h5>
                        </div>
                        <div className="col-md-6">
                            <p className="mb-1 text-muted">Descripción</p>
                            <h5>{company.description || "No especificada"}</h5>
                        </div>
                    </div>
                    <div className="row mb-3">
                        <div className="col-md-6">
                            <p className="mb-1 text-muted">País</p>
                            <h5>{company.country || "No especificado"}</h5>
                        </div>
                        <div className="col-md-6">
                            <p className="mb-1 text-muted">Fecha de Fundación</p>
                            <h5>
                                {company.founded_date
                                    ? new Date(company.founded_date).toLocaleDateString()
                                    : "No especificada"}
                            </h5>
                        </div>
                    </div>
                    <div className="row mb-3">
                        <div className="col-md-6">
                            <p className="mb-1 text-muted">Fecha de Creación</p>
                            <h5>{new Date(company.created_at).toLocaleDateString()}</h5>
                        </div>
                        <div className="col-md-6">
                            <p className="mb-1 text-muted">Última Actualización</p>
                            <h5>{new Date(company.updated_at).toLocaleDateString()}</h5>
                        </div>
                    </div>
                </div>
                <div className="card-footer bg-light text-end">
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
