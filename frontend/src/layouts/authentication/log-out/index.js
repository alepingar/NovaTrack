import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "context/AuthContext";

function Logout() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    logout();
    navigate("/authentication/sign-in");
  }, [logout, navigate]);

  return null;
}

export default Logout;
