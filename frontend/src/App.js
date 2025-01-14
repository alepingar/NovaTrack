import React from "react";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import RegisterCompany from "./components/RegisterCompany";
import Login from "./components/Login";
import Home from "./components/Home";
import Profile from "./components/Profile";
import EditProfile from "./components/EditProfile";
import ManageUsers from "./components/ManageUsers";
import "./App.css";

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/home" element={<Home role="admin" />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/edit-profile" element={<EditProfile />} />
                <Route path="/register/company" element={<RegisterCompany />} />
                <Route path="/login" element={<Login />} />
                <Route path="/" element={<Navigate to="/login"/>} />
                <Route path="/manage-users" element={<ManageUsers/>} />
            </Routes>
        </Router>
    );
}

export default App;
