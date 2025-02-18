import { useEffect } from "react";
import { useAuth } from "context/AuthContext";
import { useNavigate } from "react-router-dom";

function Logout() {
  const { logout } = useAuth();
  const Navigate = useNavigate();

  useEffect(() => {
    logout(); // Elimina el token y actualiza el estado
    Navigate("/general-dashboard");
  }, [logout]);

  return null; // No renderiza nada
}

export default Logout;
