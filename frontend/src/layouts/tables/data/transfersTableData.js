import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDBadge from "components/MDBadge";
import axios from "axios";
import { useEffect, useState, useRef } from "react";

export default function data(filter) {
  const [transfers, setTransfers] = useState([]);
  const transfersRef = useRef([]);
  const [sortColumn, setSortColumn] = useState("timestamp"); // Orden predeterminado
  const [sortDirection, setSortDirection] = useState("desc"); // Orden descendente inicial

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

  // Función para ordenar
  const handleSort = (column) => {
    if (column === sortColumn) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortColumn(column);
      setSortDirection("asc");
    }
  };

  // Aplicar la ordenación según la columna seleccionada
  const sortedTransfers = [...transfers].sort((a, b) => {
    if (sortColumn === "amount") {
      return sortDirection === "asc" ? a.amount - b.amount : b.amount - a.amount;
    } else if (sortColumn === "status") {
      // Definir prioridad de cada estado
      const statusPriority = { completada: 1, pendiente: 2, fallida: 3 };
      // Primero agrupar por estado (completadas primero, pendientes en medio, fallidas al final)
      if (statusPriority[a.status] !== statusPriority[b.status]) {
        return sortDirection === "asc"
          ? statusPriority[a.status] - statusPriority[b.status]
          : statusPriority[b.status] - statusPriority[a.status];
      }
    } else if (sortColumn === "is_anomalous") {
      // Primero ordenar por anomalía
      if (a.is_anomalous !== b.is_anomalous) {
        return sortDirection === "asc"
          ? a.is_anomalous - b.is_anomalous // No anómalas primero
          : b.is_anomalous - a.is_anomalous; // Anómalas primero
      }
      // Luego ordenar por fecha dentro de cada grupo
      return sortDirection === "asc"
        ? new Date(a.timestamp) - new Date(b.timestamp) // Más antiguas primero
        : new Date(b.timestamp) - new Date(a.timestamp); // Más recientes primero
    } else {
      return sortDirection === "asc"
        ? new Date(a.timestamp) - new Date(b.timestamp)
        : new Date(b.timestamp) - new Date(a.timestamp);
    }
  });

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
      {
        Header: (
          <MDTypography variant="h6" fontWeight="bold">
            ID
          </MDTypography>
        ),
        accessor: "id",
        align: "left",
      },
      {
        Header: (
          <MDTypography
            variant="h6"
            fontWeight="bold"
            onClick={() => handleSort("amount")}
            style={{ cursor: "pointer" }}
          >
            Monto convertido {sortColumn === "amount" ? (sortDirection === "asc" ? "↑" : "↓") : ""}
          </MDTypography>
        ),
        accessor: "amount",
        align: "left",
      },
      {
        Header: (
          <MDTypography variant="h6" fontWeight="bold">
            Moneda
          </MDTypography>
        ),
        accessor: "currency",
        align: "center",
      },
      {
        Header: (
          <MDTypography variant="h6" fontWeight="bold">
            Origen
          </MDTypography>
        ),
        accessor: "from_account",
        align: "left",
      },
      {
        Header: (
          <MDTypography
            variant="h6"
            fontWeight="bold"
            onClick={() => handleSort("timestamp")}
            style={{ cursor: "pointer" }}
          >
            Fecha {sortColumn === "timestamp" ? (sortDirection === "asc" ? "↑" : "↓") : ""}
          </MDTypography>
        ),
        accessor: "timestamp",
        align: "center",
      },
      {
        Header: (
          <MDTypography
            variant="h6"
            fontWeight="bold"
            onClick={() => handleSort("status")}
            style={{ cursor: "pointer" }}
          >
            Estado {sortColumn === "status" ? (sortDirection === "asc" ? "↑" : "↓") : ""}
          </MDTypography>
        ),
        accessor: "status",
        align: "center",
      },
      {
        Header: (
          <MDTypography
            variant="h6"
            fontWeight="bold"
            onClick={() => handleSort("is_anomalous")}
            style={{ cursor: "pointer" }}
          >
            Anómala {sortColumn === "is_anomalous" ? (sortDirection === "asc" ? "↑" : "↓") : ""}
          </MDTypography>
        ),
        accessor: "is_anomalous",
        align: "center",
      },
      {
        Header: (
          <MDTypography variant="h6" fontWeight="bold">
            Acción
          </MDTypography>
        ),
        accessor: "action",
        align: "center",
      },
    ],
    rows,
    fetchFilteredData: fetchTransfers,
  };
}
