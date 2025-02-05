import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";

function TermsOfService() {
    return (
        <div className="help-container">
            <div className="card shadow-lg p-4">
                <h1 className="text-primary text-center mb-4">Términos de Servicio</h1>
                <p className="text-muted">
                    Bienvenido a NovaTrack. Al utilizar nuestra plataforma, aceptas cumplir con los siguientes términos y condiciones.
                </p>
                <hr />

                <h2>🖥️ Uso de la Plataforma</h2>
                <p>NovaTrack proporciona herramientas para gestionar usuarios, monitorizar transacciones financieras y detectar anomalías.</p>

                <h2>🔑 Responsabilidad del Usuario</h2>
                <p>Los usuarios deben mantener la confidencialidad de sus credenciales. NovaTrack no será responsable por accesos no autorizados.</p>

                <h2>📜 Propiedad Intelectual</h2>
                <p>Todo el contenido de NovaTrack, incluidas marcas y código, es propiedad de la aplicación. Está prohibido copiar, distribuir o modificar sin autorización.</p>

                <h2>⚠️ Limitación de Responsabilidad</h2>
                <p>NovaTrack no se hace responsable de pérdidas económicas, interrupciones del servicio o daños derivados del uso de la plataforma.</p>

                <h2>📝 Modificaciones</h2>
                <p>Nos reservamos el derecho de modificar estos términos en cualquier momento. Los usuarios serán notificados de cambios importantes.</p>
            </div>
        </div>
    );
}

export default TermsOfService;
