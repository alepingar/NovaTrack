import React from "react";
import { Navigate, Outlet } from "react-router-dom";

function PrivateRoute() {
    const token = localStorage.getItem("token");

    // Si no hay token, redirigir al login
    if (!token) {
        return <Navigate to="/login" replace />;
    }

    return <Outlet />;
}

export default PrivateRoute;
