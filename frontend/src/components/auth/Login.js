import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";

function Login() {
    const [credentials, setCredentials] = useState({ email: "", password: "" });
    const [emailForReset, setEmailForReset] = useState("");
    const [showResetModal, setShowResetModal] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (token) {
            navigate("/home");
        }
    }, [navigate]);

    const handleChange = (e) => {
        setCredentials({
            ...credentials,
            [e.target.name]: e.target.value,
        });
    };

    const handleResetChange = (e) => {
        setEmailForReset(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post("http://127.0.0.1:8000/auth/login", credentials);
            alert("Inicio de sesión exitoso");

            const { access_token } = response.data;
            localStorage.setItem("token", access_token);
            navigate("/home");
        } catch (error) {
            alert("Error al iniciar sesión");
            console.error("Error:", error.response?.data || error.message);
        }
    };

    const handlePasswordReset = async () => {
        try {
            await axios.post("http://127.0.0.1:8000/auth/reset-password", { email: emailForReset });
            alert("Se ha enviado un correo para recuperar tu contraseña.");
            setShowResetModal(false);
        } catch (error) {
            alert("Error al enviar el correo de recuperación.");
            console.error("Error:", error.response?.data || error.message);
        }
    };

    return (
        <div className="container-fluid d-flex align-items-center justify-content-center vh-100 bg-light">
            <div className="row w-100">
                {/* Espacio para una futura imagen o branding en la izquierda */}
                <div className="col-lg-6 d-none d-lg-flex align-items-center justify-content-center bg-dark text-white">
                    <h1>Bienvenido a NovaTrack</h1>
                </div>
                
                {/* Formulario de inicio de sesión */}
                <div className="col-lg-6 d-flex align-items-center justify-content-center">
                    <div className="card shadow p-4" style={{ width: "100%", maxWidth: "400px" }}>
                        <h2 className="text-center mb-4">Iniciar Sesión</h2>
                        <form onSubmit={handleSubmit}>
                            <div className="mb-3">
                                <label htmlFor="email" className="form-label">Correo Electrónico</label>
                                <input
                                    type="email"
                                    className="form-control"
                                    id="email"
                                    name="email"
                                    placeholder="Correo Electrónico"
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                            <div className="mb-3">
                                <label htmlFor="password" className="form-label">Contraseña</label>
                                <input
                                    type="password"
                                    className="form-control"
                                    id="password"
                                    name="password"
                                    placeholder="Contraseña"
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                            <button type="submit" className="btn btn-primary w-100">Iniciar Sesión</button>
                        </form>
                        <div className="text-center mt-3">
                            <button
                                className="btn btn-link"
                                onClick={() => setShowResetModal(true)}
                            >
                                ¿Has olvidado tu contraseña?
                            </button>
                            <p>¿No tienes cuenta?</p>
                            <button
                                className="btn btn-secondary w-100"
                                onClick={() => navigate("/register/company")}
                            >
                                Registrarse como Empresa
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Modal para recuperación de contraseña */}
            {showResetModal && (
                <div className="modal fade show d-block" tabIndex="-1" aria-labelledby="resetModalLabel" aria-hidden="true">
                    <div className="modal-dialog modal-dialog-centered">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title" id="resetModalLabel">Recuperar Contraseña</h5>
                                <button
                                    type="button"
                                    className="btn-close"
                                    aria-label="Close"
                                    onClick={() => setShowResetModal(false)}
                                ></button>
                            </div>
                            <div className="modal-body">
                                <p>Introduce tu correo electrónico para recibir un enlace de recuperación.</p>
                                <input
                                    type="email"
                                    className="form-control"
                                    placeholder="Correo Electrónico"
                                    value={emailForReset}
                                    onChange={handleResetChange}
                                    required
                                />
                            </div>
                            <div className="modal-footer">
                                <button
                                    className="btn btn-primary"
                                    onClick={handlePasswordReset}
                                >
                                    Enviar Enlace
                                </button>
                                <button
                                    className="btn btn-secondary"
                                    onClick={() => setShowResetModal(false)}
                                >
                                    Cancelar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Login;
