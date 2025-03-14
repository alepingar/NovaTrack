import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import axios from "axios";

function ResetPassword() {
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:8000/reset-password-confirm", {
        token,
        password,
      });
      setMessage(response.data.message);
    } catch (error) {
      setMessage("Error: " + (error.response?.data?.detail || "Inténtalo de nuevo."));
    }
  };

  return (
    <div>
      <h2>Restablecer contraseña</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="password"
          placeholder="Nueva contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Cambiar contraseña</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}

export default ResetPassword;
