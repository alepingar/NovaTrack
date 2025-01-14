import React from "react";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import RegisterCompany from "./components/RegisterCompany";
import Login from "./components/Login";
import Home from "./components/Home";
import Profile from "./components/Profile";
import "./App.css";
import EditProfile from "./components/EditProfile";


function App() {
    return (
        <Router>
            <Routes>
                <Route path="/home" element={<Home role="admin" />} />
                <Route path="/register/company" element={<RegisterCompany />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/edit-profile" element={<EditProfile />} />
                <Route path="/login" element={<Login />} />
                <Route path="/" element={<Navigate to="/login"/>} />
            </Routes>
        </Router>
    );
}

export default App;
