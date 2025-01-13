import axios from "axios";
import { useState } from "react";

function Register() {
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        password: "",
        industry: "",
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post("http://localhost:8000/users/register", formData);
            alert("Registro exitoso");
            console.log(response.data);
        } catch (error) {
            alert("Error al registrar la empresa");
        }
    };

    return (
        <div>
          <h1>Registro de Empresa</h1>
          <form onSubmit={handleSubmit}>
            <label>Nombre de la Empresa:</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
    
            <label>Correo Electrónico:</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
    
            <label>Contraseña:</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
    
            <label>Industria:</label>
            <input
              type="text"
              name="industry"
              value={formData.industry}
              onChange={handleChange}
            />
    
            <button type="submit">Registrar</button>
          </form>
        </div>
      );
    }

export default Register;