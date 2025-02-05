import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";

function PrivacyPolicy() {
    return (
        <div className="help-container">
            <div className="card shadow-lg p-4">
                <h1 className="text-primary text-center mb-4">Política de Privacidad</h1>
                <p className="text-muted">En NovaTrack, valoramos tu privacidad y estamos comprometidos con proteger la información personal que compartes con nosotros.</p>
                <hr />

                <h2>📊 Información Recopilada</h2>
                <p>Recopilamos datos como nombres, correos electrónicos y actividades dentro de la aplicación para proporcionarte una experiencia optimizada.</p>

                <h2>📌 Uso de la Información</h2>
                <ul>
                    <li>Proporcionar acceso seguro a la plataforma.</li>
                    <li>Monitorizar y analizar el uso del sistema.</li>
                    <li>Detectar y prevenir anomalías.</li>
                </ul>

                <h2>🔒 Compartir Datos</h2>
                <p>No compartimos tu información con terceros, excepto cuando sea requerido por la ley o necesario para garantizar la seguridad del sistema.</p>

                <h2>🛡️ Seguridad</h2>
                <p>Empleamos medidas avanzadas de seguridad para proteger tus datos, como cifrado y autenticación segura.</p>

                <h2>✔️ Tus Derechos</h2>
                <p>Puedes solicitar acceso, modificación o eliminación de tus datos en cualquier momento poniéndote en contacto con nosotros.</p>
            </div>
        </div>
    );
}

export default PrivacyPolicy;
