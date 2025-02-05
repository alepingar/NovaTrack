import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";

function Help() {
    return (
        <div className="help-container">
            <div className="card shadow-lg p-4">
                <h1 className="text-primary text-center mb-4">Ayuda y Soporte</h1>
                <p className="text-muted">
                    Si necesitas asistencia con NovaTrack, aquí tienes una guía rápida y formas de ponerte en contacto con nuestro equipo.
                </p>
                <hr />
                <h2>🔑 Inicio de Sesión</h2>
                <p>Asegúrate de ingresar el correo electrónico y la contraseña registrados. Si olvidaste tu contraseña, contáctanos para restablecerla.</p>
                
                <h2>👥 Gestión de Usuarios</h2>
                <p>Los administradores pueden agregar, editar y eliminar usuarios desde la sección "Gestión de Usuarios". Consulta los permisos asignados a cada rol.</p>

                <h2>⚠️ Reportar Problemas</h2>
                <p>Si encuentras problemas técnicos o anomalías inesperadas, puedes enviarnos un informe a través de nuestro correo: 
                    <a href="mailto:soporte@novatrack.com" className="text-primary"> soporte@novatrack.com</a>.
                </p>

                <h2>📩 Contacto</h2>
                <p>Para preguntas o soporte técnico, envía un correo a 
                    <a href="mailto:soporte@novatrack.com" className="text-primary"> soporte@novatrack.com</a>. Te responderemos lo antes posible.
                </p>
            </div>
        </div>
    );
}

export default Help;
