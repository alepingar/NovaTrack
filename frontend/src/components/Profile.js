import React, { useEffect, useState } from "react";
import axios from "axios";

function Profile() {
    const [company, setCompany] = useState(null);

    useEffect(() => {
        const fetchCompanyData = async () => {
            try {
                const token = localStorage.getItem("token");
                const response = await axios.get("http://127.0.0.1:8000/companies/profile", {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                setCompany(response.data);
            } catch (error) {
                console.error("Error al obtener los datos de la empresa:", error);
            }
        };

        fetchCompanyData();
    }, []);

    if (!company) {
        return <p>Cargando información...</p>;
    }

    return (
        <div className="container mt-4">
            <h2>Perfil de la Empresa</h2>
            <p><strong>Nombre:</strong> {company.name}</p>
            <p><strong>Email:</strong> {company.email}</p>
            <p><strong>Industria:</strong> {company.industry || "No especificada"}</p>
        </div>
    );
}

export default Profile;
