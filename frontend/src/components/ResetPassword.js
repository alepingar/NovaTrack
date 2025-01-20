import React, { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import axios from "axios";

function ResetPassword() {
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            alert("Las contraseñas no coinciden");
            return;
        }

        try {
            const token = searchParams.get("token");
            await axios.post("http://127.0.0.1:8000/companies/reset-password-confirm", {
                token,
                password,
            });
            alert("Contraseña restablecida correctamente");
            navigate("/login");
        } catch (error) {
            alert("Error al restablecer contraseña");
            console.error(error);
        }
    };

    return (
        <div className="container mt-5">
            <div className="card shadow p-4">
                <h2>Restablecer Contraseña</h2>
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label>Nueva Contraseña</label>
                        <input
                            type="password"
                            className="form-control"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <div className="mb-3">
                        <label>Confirmar Contraseña</label>
                        <input
                            type="password"
                            className="form-control"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" className="btn btn-primary w-100">
                        Restablecer Contraseña
                    </button>
                </form>
            </div>
        </div>
    );
}

export default ResetPassword;
