import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";

function Home() {
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

    return (
        <div>
            {/* Navbar Superior */}
            <nav className="navbar navbar-expand-lg navbar-dark bg-primary px-4 shadow">
                <a className="navbar-brand fw-bold text-white" href="/">
                    NovaTrack
                </a>
                <button
                    className="navbar-toggler"
                    type="button"
                    data-bs-toggle="collapse"
                    data-bs-target="#navbarNav"
                    aria-controls="navbarNav"
                    aria-expanded="false"
                    aria-label="Toggle navigation"
                >
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse justify-content-between" id="navbarNav">
                    <ul className="navbar-nav">
                        <li className="nav-item">
                            <a className="nav-link text-white fw-bold" href="/transactions">Transacciones</a>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link text-white fw-bold" href="/anomalies">Anomalías</a>
                        </li>
                    </ul>

                    {/* Nombre de la Empresa */}
                    <div className="d-flex align-items-center">
                        {company && (
                            <div className="dropdown">
                                <button
                                    className="btn btn-light dropdown-toggle"
                                    type="button"
                                    id="profileDropdown"
                                    data-bs-toggle="dropdown"
                                    aria-expanded="false"
                                >
                                    {company.name}
                                </button>
                                <ul
                                    className="dropdown-menu dropdown-menu-end"
                                    aria-labelledby="profileDropdown"
                                >
                                    <li>
                                        <button
                                            className="dropdown-item"
                                            onClick={() => navigate("/profile")}
                                        >
                                            Ver Perfil
                                        </button>
                                    </li>
                                    <li>
                                        <button
                                            className="dropdown-item text-danger"
                                            onClick={() => {
                                                localStorage.removeItem("token");
                                                navigate("/login");
                                            }}
                                        >
                                            Cerrar Sesión
                                        </button>
                                    </li>
                                </ul>
                            </div>
                        )}
                    </div>
                </div>
            </nav>

            {/* Contenido Principal */}
            <main className="container mt-4">
                <h1 className="text-center text-primary">Bienvenido a NovaTrack</h1>
                <p className="text-center text-secondary">
                    Selecciona una sección del menú para continuar.
                </p>
            </main>
        </div>
    );
}

export default Home;
