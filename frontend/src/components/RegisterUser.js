import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";

function RegisterUser() {
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        password: "",
        company_id: "",
        role: "staff", // Por defecto, rol de personal
    });
    const [companies, setCompanies] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        // Obtener la lista de empresas para el desplegable
        const fetchCompanies = async () => {
            try {
                const response = await axios.get("http://127.0.0.1:8000/users/companies");
                setCompanies(response.data);
            } catch (error) {
                console.error("Error al cargar las empresas:", error);
            }
        };
        fetchCompanies();
    }, []);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await axios.post("http://127.0.0.1:8000/users/register/user", formData);
            alert("Registro exitoso");
            navigate("/login"); // Redirige al login tras registro exitoso
        } catch (error) {
            alert("Error al registrar el usuario");
            console.error(error);
        }
    };

    return (
        <div className="container mt-5">
            <div className="row justify-content-center">
                <div className="col-md-6">
                    <div className="card shadow">
                        <div className="card-header text-center">
                            <h2>Registro de Personal</h2>
                        </div>
                        <div className="card-body">
                            <form onSubmit={handleSubmit}>
                                <div className="mb-3">
                                    <label htmlFor="name" className="form-label">Nombre</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        id="name"
                                        name="name"
                                        placeholder="Nombre"
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
                                    <label htmlFor="company_id" className="form-label">Empresa</label>
                                    <select
                                        className="form-select"
                                        id="company_id"
                                        name="company_id"
                                        onChange={handleChange}
                                        required
                                    >
                                        <option value="">Selecciona una Empresa</option>
                                        {companies.map((company) => (
                                            <option key={company.id} value={company.id}>
                                                {company.name}
                                            </option>
                                        ))}
                                    </select>
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

export default RegisterUser;
