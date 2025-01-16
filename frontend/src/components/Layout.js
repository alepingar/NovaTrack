import React, { useEffect, useState } from "react";
import axios from "axios";
import { jwtDecode } from "jwt-decode";

import { Outlet, useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";

function Layout() {
    const [company, setCompany] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchCompanyData = async () => {
            try {
                const token = localStorage.getItem("token");

                if (!token) {
                    // Redirigir al login si no hay token
                    navigate("/login");
                    return;
                }

                // Decodificar el token para verificar su validez
                const decoded = jwtDecode(token);
                const currentTime = Date.now() / 1000;

                if (decoded.exp < currentTime) {
                    // Si el token ha expirado, redirigir al login
                    localStorage.removeItem("token");
                    navigate("/login");
                    return;
                }

                // Obtener los datos de la empresa desde el backend
                const response = await axios.get("http://127.0.0.1:8000/companies/profile", {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                setCompany(response.data);
            } catch (error) {
                console.error("Error al obtener los datos de la empresa:", error);
                localStorage.removeItem("token");
                navigate("/login");
            }
        };

        fetchCompanyData();
    }, [navigate]);

    if (!company) {
        return (
            <div className="container mt-4 text-center">
                <p>Cargando...</p>
            </div>
        );
    }

    return (
        <div>
            {/* Navbar Superior */}
            <nav className="navbar navbar-expand-lg navbar-dark bg-primary px-4 shadow">
                <a className="navbar-brand fw-bold text-white" href="/home">
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
                            <a className="nav-link text-white fw-bold" href="/transfers">Transacciones</a>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link text-white fw-bold" href="/anomalies">Anomalías</a>
                        </li>
                        {company && company.role === "admin" && (
                            <li className="nav-item">
                                <a className="nav-link text-white fw-bold" href="/manage-users">Gestión de Usuarios</a>
                            </li>
                        )}
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
                <Outlet />
            </main>
        </div>
    );
}

export default Layout;
