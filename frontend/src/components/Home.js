import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "./../App.css";

function Home() {
    return (
        <div>
            {/* Navbar Superior */}
            <nav className="navbar navbar-expand-lg navbar-light bg-light px-4 shadow">
                <a className="navbar-brand fw-bold" href="/">
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
                    {/* Links de navegación */}
                    <ul className="navbar-nav">
                        <li className="nav-item">
                            <a className="nav-link" href="/profile">Perfil</a>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link" href="/transactions">Transacciones</a>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link" href="/anomalies">Anomalías</a>
                        </li>
                    </ul>
                </div>
            </nav>

            {/* Contenido Principal */}
            <main className="container mt-4">
                <h1 className="text-center">Bienvenido a NovaTrack</h1>
                <p className="text-center">Selecciona una sección del menú para continuar.</p>
            </main>
        </div>
    );
}

export default Home;
