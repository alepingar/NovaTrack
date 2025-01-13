import React from "react";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import RegisterCompany from "./components/RegisterCompany";
import RegisterUser from "./components/RegisterUser";
import Login from "./components/Login";
import Home from "./components/Home";

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/home" element={<Home role="admin" />} />
                <Route path="/register/user" element={<RegisterUser />} />
                <Route path="/register/company" element={<RegisterCompany />} />
                <Route path="/login" element={<Login />} />
                <Route path="/" element={<Navigate to="/login"/>} />
            </Routes>
        </Router>
    );
}

export default App;
