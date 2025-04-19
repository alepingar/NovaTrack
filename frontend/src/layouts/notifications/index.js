import { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDAlert from "components/MDAlert";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import axios from "axios";
import { format } from "date-fns";

function Notifications() {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const token = localStorage.getItem("token");
        const notiRes = await axios.get(`${process.env.REACT_APP_API_URL}/notifications`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setNotifications(notiRes.data);
      } catch (error) {
        console.error("Error fetching notifications:", error);
      }
    };
    fetchNotifications();
  }, []);

  const handleDeleteNotification = async (notificationId) => {
    try {
      const token = localStorage.getItem("token");
      await axios.delete(`${process.env.REACT_APP_API_URL}/notifications/${notificationId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setNotifications((prevNotifications) =>
        prevNotifications.filter((notif) => notif._id !== notificationId)
      );
    } catch (error) {
      console.error("Error deleting notification:", error);
    }
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox
        sx={{
          display: "flex",
          flexDirection: "column",
          flexGrow: 1, // Expande el contenido para empujar el footer
          minHeight: "calc(100vh - 64px)", // Ajusta al 100% menos la navbar
        }}
      >
        <MDBox mt={6} mb={3} sx={{ flexGrow: 1 }}>
          <Grid container spacing={3} justifyContent="center">
            <Grid item xs={12} lg={8}>
              <Card>
                <MDBox p={2}>
                  <MDTypography variant="h5">Alertas</MDTypography>
                </MDBox>
                <MDBox pt={2} px={2}>
                  {notifications.length === 0 ? (
                    <MDTypography variant="body2" color="text">
                      No hay notificaciones nuevas ahora mismo.
                    </MDTypography>
                  ) : (
                    notifications.map((notif) => (
                      <div
                        key={notif._id}
                        style={{
                          marginBottom: "10px",
                          padding: "10px",
                          backgroundColor: "#f44336",
                          color: "white",
                          position: "relative",
                        }}
                      >
                        <MDTypography variant="body2" color="white">
                          {notif.message}
                        </MDTypography>
                        <MDTypography variant="body2" color="white">
                          {format(new Date(notif.timestamp), "dd/MM/yyyy HH:mm")}
                        </MDTypography>
                        <button
                          onClick={() => {
                            handleDeleteNotification(notif._id);
                          }}
                          style={{
                            position: "absolute",
                            top: "5px",
                            right: "5px",
                            backgroundColor: "transparent",
                            border: "none",
                            color: "white",
                            cursor: "pointer",
                          }}
                        >
                          X
                        </button>
                      </div>
                    ))
                  )}
                </MDBox>
              </Card>
            </Grid>
          </Grid>
        </MDBox>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Notifications;
