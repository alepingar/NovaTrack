import React from "react";

function Footer() {
    return (
        <footer className="bg-dark text-white py-3 mt-auto">
            <div className="container text-center">
                {/* Links rápidos */}
                <div className="mb-2">
                    <a href="/terms" className="text-white mx-3 text-decoration-none">
                        Términos de Servicio
                    </a>
                    <a href="/privacy" className="text-white mx-3 text-decoration-none">
                        Política de Privacidad
                    </a>
                    <a href="/help" className="text-white mx-3 text-decoration-none">
                        Ayuda / Soporte
                    </a>
                </div>

                {/* Información de derechos */}
                <p className="mb-0">
                    &copy; {new Date().getFullYear()} NovaTrack. Todos los derechos reservados.
                </p>
            </div>
        </footer>
    );
}

export default Footer;
