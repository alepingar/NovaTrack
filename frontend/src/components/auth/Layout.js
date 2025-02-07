import React, { useEffect, useState } from "react";
import axios from "axios";
import { jwtDecode } from "jwt-decode";
import { Outlet, useNavigate } from "react-router-dom";
import Footer from "../footer/Footer";
import "bootstrap/dist/css/bootstrap.min.css";
import '../../css/App.css';
import { Badge, Dropdown, List } from "antd";
import { BellOutlined } from "@ant-design/icons";

function Layout() {
    const [userData, setUserData] = useState(null);
    const [anomalies, setAnomalies] = useState([]);
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
                        : "http://127.0.0.1:8000/users/profile";

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

    // 🔥 Conectar con WebSocket para recibir anomalías en tiempo real
    useEffect(() => {
        const ws = new WebSocket("ws://127.0.0.1:8000/ws/anomalies");

        ws.onmessage = (event) => {
            const anomaly = JSON.parse(event.data);
            console.log("⚠️ Nueva anomalía detectada:", anomaly);
            setAnomalies((prev) => [anomaly, ...prev]);
        };

        return () => ws.close();
    }, []);

    if (!userData) {
        return <div className="text-center mt-5">Cargando...</div>;
    }

    const notificationsMenu = (
        <List
            dataSource={anomalies}
            renderItem={(item) => (
                <List.Item>
                    <strong>Monto:</strong> ${item.amount} - <strong>Estado:</strong> {item.status}
                </List.Item>
            )}
        />
    );

    return (
        <div className="d-flex flex-column" style={{ minHeight: "100vh" }}>
            {/* Navbar */}
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
                            {/* ✅ REINTEGRADO: Gestión de Usuarios para Admins */}
                            {userData?.role === "admin" && (
                                <li className="nav-item">
                                    <a className="nav-link text-white" href="/manage-users">
                                        <i className="bi bi-people me-1"></i>Gestión de Usuarios
                                    </a>
                                </li>
                            )}
                        </ul>

                        {/* 🔔 Notificaciones */}
                        <Dropdown overlay={notificationsMenu} trigger={["click"]}>
                            <Badge count={anomalies.length} offset={[10, 0]}>
                                <BellOutlined style={{ fontSize: "24px", color: "#fff", cursor: "pointer", marginRight: "20px" }} />
                            </Badge>
                        </Dropdown>

                        {/* Perfil */}
                        <div className="d-flex align-items-center">
                            {userData && (
                                <div className="dropdown d-flex align-items-center">
                                    <button className="btn btn-light dropdown-toggle" type="button" id="profileDropdown"
                                        data-bs-toggle="dropdown" aria-expanded="false">
                                        {userData.name}
                                    </button>
                                    <ul className="dropdown-menu dropdown-menu-end" aria-labelledby="profileDropdown">
                                        <li><button className="dropdown-item" onClick={() => navigate("/profile")}>Ver Perfil</button></li>
                                        <li><button className="dropdown-item text-danger"
                                            onClick={() => { localStorage.removeItem("token"); navigate("/login"); }}>Cerrar Sesión</button></li>
                                    </ul>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </nav>

            {/* Contenido */}
            <main className="flex-grow-1 container mt-5 pt-4">
                <Outlet />
            </main>

            {/* Footer */}
            <Footer />
        </div>
    );
}

export default Layout;
