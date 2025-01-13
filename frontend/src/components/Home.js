import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";

function Home({ role }) {
    // El role puede ser "admin" para empresas o "staff" para personal
    return (
        <div className="d-flex">
            {/* Panel de navegación lateral */}
            <nav className="bg-light p-3" style={{ width: "250px", height: "100vh" }}>
                <h4>Menú</h4>
                <ul className="nav flex-column">
                    <li className="nav-item">
                        <a href="#summary" className="nav-link">Resumen</a>
                    </li>
                    {role === "admin" && (
                        <li className="nav-item">
                            <a href="#users" className="nav-link">Gestión de Usuarios</a>
                        </li>
                    )}
                    <li className="nav-item">
                        <a href="#transactions" className="nav-link">Transacciones</a>
                    </li>
                    <li className="nav-item">
                        <a href="#anomalies" className="nav-link">Anomalías</a>
                    </li>
                    <li className="nav-item">
                        <a href="#settings" className="nav-link">Configuración</a>
                    </li>
                </ul>
            </nav>

            {/* Contenido principal */}
            <main className="p-4" style={{ flex: 1 }}>
                <div id="summary">
                    <h2>Resumen General</h2>
                    <p>Gráficos y estadísticas de actividad reciente.</p>
                </div>
                {role === "admin" && (
                    <div id="users">
                        <h2>Gestión de Usuarios</h2>
                        <p>Añadir, eliminar y gestionar empleados.</p>
                    </div>
                )}
                <div id="transactions">
                    <h2>Historial de Transacciones</h2>
                    <p>Tabla de transacciones recientes.</p>
                </div>
                <div id="anomalies">
                    <h2>Análisis de Anomalías</h2>
                    <p>Lista y estadísticas de anomalías detectadas.</p>
                </div>
                <div id="settings">
                    <h2>Configuraciones</h2>
                    <p>Opciones de personalización de cuenta y criterios de detección.</p>
                </div>
            </main>
        </div>
    );
}

export default Home;
