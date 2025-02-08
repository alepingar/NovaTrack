import { createContext, useContext, useState, useEffect } from "react";
import PropTypes from "prop-types";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Actualizar el estado de autenticación
  const updateAuthState = () => {
    const token = localStorage.getItem("token");
    setIsAuthenticated(!!token);
  };

  useEffect(() => {
    updateAuthState(); // Inicializar el estado al cargar

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
