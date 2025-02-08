import { useEffect } from "react";
import { useAuth } from "context/AuthContext";

function Logout() {
  const { logout } = useAuth();

  useEffect(() => {
    logout(); // Elimina el token y actualiza el estado
  }, [logout]);

  return null; // No renderiza nada
}

export default Logout;
