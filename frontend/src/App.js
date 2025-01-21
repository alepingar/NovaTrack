import React from "react";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import RegisterCompany from "./components/company/RegisterCompany";
import Login from "./components/auth/Login";
import Home from "./components/auth/Home";
import Profile from "./components/company/Profile";
import EditProfile from "./components/company/EditProfile";
import ManageUsers from "./components/user/ManageUsers";
import Layout from "./components/auth/Layout";
import PrivateRoute from "./components/auth/PrivateRoute";
import Transfers from "./components/transfer/Transfers";
import TransferDetails from "./components/transfer/TransferDetails";
import Help from "./components/footer/Help";
import PrivacyPolicy from "./components/footer/PrivacyPolicy";
import TermsOfService from "./components/footer/TermsOfService";
import "./css/App.css";

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

                {/* Rutas pública: Footer */}
                <Route path="/terms" element={<TermsOfService />} />
                <Route path="/privacy" element={<PrivacyPolicy />} />
                <Route path="/help" element={<Help />} />

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
                    <Route path="/transfers/:id" element={<TransferDetails />} />
                </Route>
            </Routes>
        </Router>
    );
}

export default App;
