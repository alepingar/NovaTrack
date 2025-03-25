import { createContext, useContext, useState, useEffect } from "react";
import PropTypes from "prop-types";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const navigate = useNavigate(); // Hook de navegación de react-router-dom
  // Actualizar el estado de autenticación
  const updateAuthState = () => {
    const token = localStorage.getItem("token");
    setIsAuthenticated(!!token);
  };

  useEffect(() => {
    updateAuthState(); // Inicializar el estado al cargar
    // Verificar si el token ha expirado
    const token = localStorage.getItem("token");
    if (token) {
      try {
        const decoded = jwtDecode(token);
        const currentTime = Date.now() / 1000;
        if (decoded.exp < currentTime) {
          logout();
          navigate("/general-dashboard");
        }
      } catch (error) {
        console.error("Error al decodificar el token:", error);
        logout(); // Si hay un error al decodificar, cerrar sesión
      }
    }
    // Listener para detectar cambios en localStorage
    const handleStorageChange = () => updateAuthState();
    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  const login = (token) => {
    localStorage.setItem("token", token);
    updateAuthState();
  };

  const logout = () => {
    localStorage.removeItem("token");
    updateAuthState();
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export function useAuth() {
  return useContext(AuthContext);
}
