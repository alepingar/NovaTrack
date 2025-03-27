import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDBadge from "components/MDBadge";
import axios from "axios";
import { useEffect, useState, useRef } from "react";

export default function data(filter) {
  const [transfers, setTransfers] = useState([]);
  const transfersRef = useRef([]);

  const fetchTransfers = async (range) => {
    try {
      const token = localStorage.getItem("token");
      let url = "http://127.0.0.1:8000/transfers";
      if (range && range !== "all") {
        const endDate = new Date();
        let startDate;
        if (range === "week") startDate = new Date(endDate.getTime() - 7 * 24 * 60 * 60 * 1000);
        if (range === "month")
          startDate = new Date(endDate.getFullYear(), endDate.getMonth() - 1, endDate.getDate());
        if (range === "3months")
          startDate = new Date(endDate.getFullYear(), endDate.getMonth() - 3, endDate.getDate());
        if (range === "year")
          startDate = new Date(endDate.getFullYear() - 1, endDate.getMonth(), endDate.getDate());
        url = `http://127.0.0.1:8000/transfers/filter/range?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}`;
      } else if (range === "all") {
        url = "http://127.0.0.1:8000/transfers/filter/all";
      }
      const response = await axios.get(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (JSON.stringify(response.data) !== JSON.stringify(transfersRef.current)) {
        transfersRef.current = response.data;
        setTransfers(response.data);
      }
    } catch (error) {
      console.error("Error al obtener las transferencias:", error);
    }
  };

  useEffect(() => {
    fetchTransfers(filter);
  }, [filter]);

  const sortedTransfers = [...transfers].sort(
    (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
  );

  const rows = sortedTransfers.map((transfer) => ({
    id: transfer.id.slice(0, 8),
    amount: (
      <MDTypography variant="caption" fontWeight="medium">
        {transfer.amount.toLocaleString("es-ES", {
          style: "currency",
          currency: "EUR",
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
    timestamp: (
      <MDTypography variant="caption">{new Date(transfer.timestamp).toLocaleString()}</MDTypography>
    ),
    status: (
      <MDBox ml={-1}>
        <MDBadge
          badgeContent={
            transfer.status === "completada"
              ? "Completada"
              : transfer.status === "pendiente"
              ? "Pendiente"
              : "Fallida"
          }
          color={
            transfer.status === "completada"
              ? "success"
              : transfer.status === "pendiente"
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
      { Header: "Monto convertido", accessor: "amount", align: "left" },
      { Header: "Moneda", accessor: "currency", align: "center" },
      { Header: "De", accessor: "from_account", align: "left" },
      { Header: "Fecha", accessor: "timestamp", align: "center" },
      { Header: "Estado", accessor: "status", align: "center" },
      { Header: "Anómala", accessor: "is_anomalous", align: "center" },
      { Header: "Acción", accessor: "action", align: "center" },
    ],
    rows,
    fetchFilteredData: fetchTransfers,
  };
}
