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
import "./App.css";

function App() {
    return (
        <Router>
            <Routes>
                {/* Redirigir automáticamente al login si está en "/" */}
                <Route path="/" element={<Navigate to="/login" replace />} />
                
                <Route path="/login" element={<Login />} />

                <Route path="/" element={<PrivateRoute />}>
                    <Route element={<Layout />}>
                        <Route path="/home" element={<Home role="admin" />} />
                        <Route path="/profile" element={<Profile />} />
                        <Route path="/edit-profile" element={<EditProfile />} />
                        <Route path="/register/company" element={<RegisterCompany />} />
                        <Route path="/manage-users" element={<ManageUsers />} />
                    </Route>
                </Route>
            </Routes>
        </Router>
    );
}

export default App;
