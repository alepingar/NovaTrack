import React from "react";
import { Navigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";

function PrivateRoute({ children }) {
    const token = localStorage.getItem("token");

    if (!token) {
        return <Navigate to="/login" replace />;
    }

    try {
        const decoded = jwtDecode(token);
        const currentTime = Date.now() / 1000;

        if (decoded.exp < currentTime) {
            // Si el token ha expirado
            localStorage.removeItem("token");
            return <Navigate to="/login" replace />;
        }

        // Si el token es válido, permite el acceso
        return children;
    } catch (error) {
        console.error("Error al decodificar el token:", error);
        localStorage.removeItem("token");
        return <Navigate to="/login" replace />;
    }
}

export default PrivateRoute;
