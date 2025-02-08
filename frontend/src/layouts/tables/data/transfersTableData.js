/* eslint-disable react/prop-types */
/* eslint-disable react/function-component-definition */
/**
=========================================================
* Material Dashboard 2 React - v2.2.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-dashboard-react
* Copyright 2023 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

/* eslint-disable react/prop-types */
/* eslint-disable react/function-component-definition */

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDBadge from "components/MDBadge";
import axios from "axios";
import { useEffect, useState } from "react";

export default function data() {
  const [transfers, setTransfers] = useState([]);

  useEffect(() => {
    const fetchTransfers = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get("http://127.0.0.1:8000/transfers", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setTransfers(response.data);
      } catch (error) {
        console.error("Error al obtener las transferencias:", error);
      }
    };

    fetchTransfers();
    const interval = setInterval(fetchTransfers, 5000); // Actualizar cada 5 segundos
    return () => clearInterval(interval); // Limpiar intervalo al desmontar
  }, []);

  const rows = transfers.map((transfer) => ({
    id: transfer.id,
    amount: (
      <MDTypography variant="caption" fontWeight="medium">
        {transfer.amount.toLocaleString("es-ES", {
          style: "currency",
          currency: transfer.currency || "EUR",
        })}
      </MDTypography>
    ),
    currency: (
      <MDTypography variant="caption" fontWeight="medium">
        {transfer.currency || "N/A"}
      </MDTypography>
    ),
    from_account: (
      <MDTypography variant="caption" fontWeight="medium">
        {transfer.from_account}
      </MDTypography>
    ),
    to_account: (
      <MDTypography variant="caption" fontWeight="medium">
        {transfer.to_account}
      </MDTypography>
    ),
    timestamp: (
      <MDTypography variant="caption">{new Date(transfer.timestamp).toLocaleString()}</MDTypography>
    ),
    status: (
      <MDBox ml={-1}>
        <MDBadge
          badgeContent={
            transfer.status === "completed"
              ? "Completada"
              : transfer.status === "pending"
              ? "Pendiente"
              : "Fallida"
          }
          color={
            transfer.status === "completed"
              ? "success"
              : transfer.status === "pending"
              ? "warning"
              : "error"
          }
          variant="gradient"
          size="sm"
        />
      </MDBox>
    ),
    is_anomalous: (
      <MDBadge
        badgeContent={transfer.is_anomalous ? "Sí" : "No"}
        color={transfer.is_anomalous ? "error" : "success"}
        variant="gradient"
        size="sm"
      />
    ),
    action: (
      <MDTypography
        component="a"
        href={`/transfers/${transfer.id}`}
        variant="caption"
        color="info"
        fontWeight="medium"
      >
        Ver Detalles
      </MDTypography>
    ),
  }));

  return {
    columns: [
      { Header: "ID", accessor: "id", align: "left" },
      { Header: "Monto", accessor: "amount", align: "left" },
      { Header: "Moneda", accessor: "currency", align: "center" },
      { Header: "De", accessor: "from_account", align: "left" },
      { Header: "Para", accessor: "to_account", align: "left" },
      { Header: "Fecha", accessor: "timestamp", align: "center" },
      { Header: "Estado", accessor: "status", align: "center" },
      { Header: "Anómala", accessor: "is_anomalous", align: "center" },
      { Header: "Acción", accessor: "action", align: "center" },
    ],
    rows,
  };
}
