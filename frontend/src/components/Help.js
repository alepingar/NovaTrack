import React from "react";

function Help() {
    return (
        <div className="container mt-5">
            <h1>Ayuda y Soporte</h1>
            <p>
                Si necesitas asistencia con NovaTrack, aquí tienes una guía rápida y formas de ponerte en contacto con nuestro equipo.
            </p>
            <h2>1. Inicio de Sesión</h2>
            <p>
                Asegúrate de ingresar el correo electrónico y la contraseña registrados. Si olvidaste tu contraseña, contáctanos para restablecerla.
            </p>
            <h2>2. Gestión de Usuarios</h2>
            <p>
                Los administradores pueden agregar, editar y eliminar usuarios desde la sección "Gestión de Usuarios". Consulta los permisos asignados a cada rol.
            </p>
            <h2>3. Reportar Problemas</h2>
            <p>
                Si encuentras problemas técnicos o anomalías inesperadas, puedes enviarnos un informe a través de nuestro correo: soporte@novatrack.com.
            </p>
            <h2>4. Contacto</h2>
            <p>
                Para preguntas o soporte técnico, envía un correo a <a href="mailto:soporte@novatrack.com">soporte@novatrack.com</a>. Te responderemos lo antes posible.
            </p>
        </div>
    );
}

export default Help;
