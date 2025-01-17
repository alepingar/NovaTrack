import React, { useEffect, useState } from "react";
import axios from "axios";
import { jwtDecode } from "jwt-decode";
import { Outlet, useNavigate } from "react-router-dom";
import Footer from "./footer/Footer";
import "bootstrap/dist/css/bootstrap.min.css";
import '../App.css'; // Importa los estilos

function Layout() {
    const [userData, setUserData] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const token = localStorage.getItem("token");

                if (!token) {
                    navigate("/login");
                    return;
                }

                const decoded = jwtDecode(token);
                const currentTime = Date.now() / 1000;

                if (decoded.exp < currentTime) {
                    localStorage.removeItem("token");
                    navigate("/login");
                    return;
                }

                const endpoint =
                    decoded.role === "admin"
                        ? "http://127.0.0.1:8000/companies/profile"
                        : "http://127.0.0.1:8000/companies/users/profile";

                const response = await axios.get(endpoint, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                setUserData({ ...response.data, role: decoded.role });
            } catch (error) {
                console.error("Error al obtener los datos:", error);
                localStorage.removeItem("token");
                navigate("/login");
            }
        };

        fetchData();
    }, [navigate]);

    if (!userData) {
        return <div className="text-center mt-5">Cargando...</div>;
    }

    return (
        <div className="d-flex flex-column" style={{ minHeight: "100vh" }}>
            {/* Navbar Superior */}
            <nav className="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
                <div className="container-fluid">
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
                                <a className="nav-link text-white" href="/transfers">
                                    <i className="bi bi-currency-exchange me-1"></i>Transacciones
                                </a>
                            </li>
                            <li className="nav-item">
                                <a className="nav-link text-white" href="/anomalies">
                                    <i className="bi bi-exclamation-circle me-1"></i>Anomalías
                                </a>
                            </li>
                            {userData?.role === "admin" && (
                                <li className="nav-item">
                                    <a className="nav-link text-white" href="/manage-users">
                                        <i className="bi bi-people me-1"></i>Gestión de Usuarios
                                    </a>
                                </li>
                            )}
                        </ul>

                        {/* Perfil del usuario o empresa */}
                        <div className="d-flex align-items-center">
                            {userData && (
                                <div className="dropdown d-flex align-items-center">
                                    <img
                                        src={userData.profileImage || "default-avatar.png"}
                                        alt="Foto de perfil"
                                        className="rounded-circle"
                                        style={{
                                            width: "40px",
                                            height: "40px",
                                            objectFit: "cover",
                                            marginRight: "10px",
                                        }}
                                    />
                                    <button
                                        className="btn btn-light dropdown-toggle"
                                        type="button"
                                        id="profileDropdown"
                                        data-bs-toggle="dropdown"
                                        aria-expanded="false"
                                    >
                                        {userData.name}
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
                </div>
            </nav>

            {/* Contenido Principal */}
            <main className="flex-grow-1 container mt-5 pt-4">
                <Outlet />
            </main>

            {/* Footer */}
            <Footer />
        </div>
    );
}

export default Layout;
