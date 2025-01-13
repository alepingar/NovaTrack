import React, { useState } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css"; // Asegúrate de que Bootstrap esté importado

function Register() {
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        password: "",
        industry: "",
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post("http://127.0.0.1:8000/users/register", formData);
            alert("Registro exitoso");
        } catch (error) {
            alert("Error al registrar la empresa");
            console.error(error);
        }
    };

    return (
        <div className="container mt-5">
            <div className="row justify-content-center">
                <div className="col-md-6">
                    <div className="card shadow">
                        <div className="card-header text-center">
                            <h2>Registro de Empresa</h2>
                        </div>
                        <div className="card-body">
                            <form onSubmit={handleSubmit}>
                                <div className="mb-3">
                                    <label htmlFor="name" className="form-label">Nombre de la Empresa</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        id="name"
                                        name="name"
                                        placeholder="Nombre de la Empresa"
                                        onChange={handleChange}
                                        required
                                    />
                                </div>
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
                                <div className="mb-3">
                                    <label htmlFor="industry" className="form-label">Industria</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        id="industry"
                                        name="industry"
                                        placeholder="Industria"
                                        onChange={handleChange}
                                    />
                                </div>
                                <button type="submit" className="btn btn-primary w-100">Registrar</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Register;
