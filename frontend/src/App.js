import React from "react";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import RegisterCompany from "./components/RegisterCompany";
import Login from "./components/Login";
import Home from "./components/Home";
import Profile from "./components/Profile";
import EditProfile from "./components/EditProfile";
import ManageUsers from "./components/ManageUsers";
import Layout from "./components/Layout";
import PrivateRoute from "./components/PrivateRoute";
import Transfers from "./components/Transfers";
import "./App.css";

function App() {
    return (
        <Router>
            <Routes>
                {/* Redirige a /login por defecto */}
                <Route path="/" element={<Navigate to="/login" replace />} />

                {/* Ruta pública: Login */}
                <Route path="/login" element={<Login />} />

                {/* Ruta pública: Registro */}
                <Route path="/register/company" element={<RegisterCompany />} />

                {/* Rutas protegidas */}
                <Route
                    path="/"
                    element={
                        <PrivateRoute>
                            <Layout />
                        </PrivateRoute>
                    }
                >
                    <Route path="/home" element={<Home />} />
                    <Route path="/profile" element={<Profile />} />
                    <Route path="/edit-profile" element={<EditProfile />} />
                    <Route path="/manage-users" element={<ManageUsers />} />
                    <Route path="/transfers" element={<Transfers />} />
                </Route>
            </Routes>
        </Router>
    );
}

export default App;
