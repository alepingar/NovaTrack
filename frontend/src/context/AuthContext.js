import { createContext, useContext, useState, useEffect } from "react";
import PropTypes from "prop-types";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Verificar si hay un token en localStorage al cargar la aplicación
    const token = localStorage.getItem("token");
    setIsAuthenticated(!!token);
  }, []);

  const login = (token) => {
    localStorage.setItem("token", token);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// Validar las props con PropTypes
AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

// Hook para usar el contexto
export function useAuth() {
  return useContext(AuthContext);
}
