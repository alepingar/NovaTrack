import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import Card from "@mui/material/Card";
import Switch from "@mui/material/Switch";
import Button from "@mui/material/Button";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import Tooltip from "@mui/material/Tooltip";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";

function PlatformSettings() {
  const [settings, setSettings] = useState({
    consent: false,
  });
  const [deleteRequest, setDeleteRequest] = useState(false);
  const [gdprActions, setGdprActions] = useState({});

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const token = localStorage.getItem("token");
        // Fetch privacy settings
        const response = await axios.get("http://127.0.0.1:8000/companies/data-sharing-consent", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (response.data) {
          setSettings({
            consent: response.data.data_sharing_consent ?? false,
          });
        }

        // Fetch account deletion request status
        const responseDelete = await axios.get("http://127.0.0.1:8000/companies/account/delete", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setDeleteRequest(responseDelete.data.account_deletion_requested ?? false);

        // Fetch GDPR request logs
        const responseGdprLogs = await axios.get("http://127.0.0.1:8000/companies/gdpr/logs", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        // Check if there are access or delete actions already requested
        const logs = responseGdprLogs.data || [];
        const actions = logs.reduce((acc, log) => {
          if (log.action === "access" || log.action === "delete") {
            acc[log.action] = true;
          }
          return acc;
        }, {});
        setGdprActions(actions);
      } catch (error) {
        console.error("Error al obtener configuraciones:", error);
        toast.error("Error al cargar configuraciones de privacidad");
      }
    };

    fetchSettings();
  }, []);

  const handleToggle = async (consentKey) => {
    try {
      const token = localStorage.getItem("token");
      const newValue = !settings[consentKey];
      setSettings((prev) => ({ ...prev, [consentKey]: newValue }));

      const payload = {
        consent: newValue,
      };
      await axios.put("http://127.0.0.1:8000/companies/data-sharing-consent", payload, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      toast.success("Preferencia actualizada correctamente");
    } catch (error) {
      console.error("Error al actualizar el consentimiento:", error);
      toast.error("Error al actualizar la preferencia");
    }
  };

  const handleGdprRequest = async (action) => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(
        "http://127.0.0.1:8000/companies/gdpr/request",
        { action },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      toast.success("Solicitud enviada correctamente");
    } catch (error) {
      console.error("Error al realizar la solicitud GDPR:", error);
      toast.error("Error en la solicitud GDPR");
    }
  };

  const handleDelete = async () => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(
        "http://127.0.0.1:8000/companies/account/delete",
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      toast.success("Solicitud de eliminación de cuenta enviada correctamente");
    } catch (error) {
      console.error("Error al realizar la solicitud:", error);
      toast.error("Error en la solicitud");
    }
  };

  return (
    <Card sx={{ boxShadow: "none" }}>
      <MDBox p={2}>
        <MDTypography variant="h6" fontWeight="medium" textTransform="capitalize">
          Configuraciones de privacidad y GDPR
        </MDTypography>
      </MDBox>
      <MDBox pt={1} pb={2} px={2} lineHeight={1.25}>
        <MDTypography variant="caption" fontWeight="bold" color="text" textTransform="uppercase">
          Consentimiento
          <Tooltip title="Al activar este switch, aceptas compartir tus datos personales para el uso de nuestros servicios.">
            <HelpOutlineIcon fontSize="small" sx={{ ml: 1, cursor: "pointer" }} />
          </Tooltip>
        </MDTypography>
        <MDBox display="flex" alignItems="center" mb={0.5} ml={-1.5}>
          <MDBox mt={0.5}>
            <Switch checked={settings.consent} onChange={() => handleToggle("consent")} />
          </MDBox>
          <MDBox width="80%" ml={0.5}>
            <MDTypography variant="button" fontWeight="regular" color="text">
              Acepto compartir mis datos para el uso de los servicios de la plataforma
            </MDTypography>
          </MDBox>
        </MDBox>

        <MDBox mt={3}>
          <MDTypography variant="caption" fontWeight="bold" color="text" textTransform="uppercase">
            Solicitudes GDPR
            <Tooltip title="Aquí puedes solicitar el acceso o la eliminación de tus datos personales según la normativa GDPR. Las solicitudes serán procesadas en un plazo de 14 días, siendo estas respondidas al correo de contacto dado">
              <HelpOutlineIcon fontSize="small" sx={{ ml: 1, cursor: "pointer" }} />
            </Tooltip>
          </MDTypography>
        </MDBox>

        <MDBox mt={1}>
          {gdprActions.access ? (
            <Button variant="contained" color="white" fullWidth disabled>
              Ya has solicitado acceso a tus datos
            </Button>
          ) : (
            <Button
              variant="contained"
              color="white"
              fullWidth
              onClick={() => handleGdprRequest("access")}
            >
              Solicitar acceso a mis datos
            </Button>
          )}
        </MDBox>
        <MDBox mt={1}>
          {gdprActions.delete ? (
            <Button variant="contained" color="white" fullWidth disabled>
              Ya has solicitado eliminación de datos
            </Button>
          ) : (
            <Button
              variant="contained"
              color="white"
              fullWidth
              onClick={() => handleGdprRequest("delete")}
            >
              Solicitar eliminación de datos
            </Button>
          )}
        </MDBox>
        <MDBox mt={1}>
          {deleteRequest ? (
            <Button variant="contained" color="white" fullWidth disabled>
              Tu cuenta ya ha sido marcada para la eliminación
            </Button>
          ) : (
            <Button variant="contained" color="error" fullWidth onClick={handleDelete}>
              Eliminar cuenta
            </Button>
          )}
        </MDBox>
      </MDBox>
    </Card>
  );
}

export default PlatformSettings;
