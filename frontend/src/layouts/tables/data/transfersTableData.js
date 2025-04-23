// En layouts/tables/data/transfersTableData.js

import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDBadge from "components/MDBadge";
import axios from "axios";
import dayjs from "dayjs";
import { useEffect, useState, useCallback } from "react";

export default function useTransfersTableData() {
  const [transfers, setTransfers] = useState([]);
  const [loading, setLoading] = useState(false); // Añadir estado de carga
  const [error, setError] = useState(null); // Añadir estado de error

  const [sortColumn, setSortColumn] = useState("timestamp");
  const [sortDirection, setSortDirection] = useState("desc");

  const fetchFilteredTransfers = useCallback(async (currentFilters = {}) => {
    setLoading(true);
    setError(null);
    console.log("Fetching table data with filters:", currentFilters); // Log para depurar

    const token = localStorage.getItem("token");
    const headers = { Authorization: `Bearer ${token}` };
    const queryParams = new URLSearchParams();

    if (currentFilters.startDate)
      queryParams.append("start_date", dayjs(currentFilters.startDate).toISOString());
    if (currentFilters.endDate)
      queryParams.append("end_date", dayjs(currentFilters.endDate).toISOString());
    if (currentFilters.bankPrefix && currentFilters.bankPrefix.trim() !== "")
      queryParams.append("bank_prefix", currentFilters.bankPrefix.trim());
    if (currentFilters.minAmount && currentFilters.minAmount.trim() !== "")
      queryParams.append("min_amount", currentFilters.minAmount.trim());
    if (currentFilters.maxAmount && currentFilters.maxAmount.trim() !== "")
      queryParams.append("max_amount", currentFilters.maxAmount.trim());

    const queryString = queryParams.toString();

    const apiUrl = `${process.env.REACT_APP_API_URL}/transfers/filtered-list${
      queryString ? `?${queryString}` : ""
    }`;

    try {
      const response = await axios.get(apiUrl, { headers });
      setTransfers(response.data || []); // Actualiza el estado con los datos recibidos
    } catch (err) {
      console.error("Error fetching filtered transfers:", err);
      setError(err.response?.data?.detail || "Error al cargar las transferencias.");
      setTransfers([]); // Limpia la tabla en caso de error
    } finally {
      setLoading(false);
    }
  }, []); // useCallback para que la función no se recree innecesariamente

  // Efecto para cargar datos iniciales (sin filtros) al montar el componente
  useEffect(() => {
    fetchFilteredTransfers({}); // Llama sin filtros al inicio
  }, [fetchFilteredTransfers]); // Depende de la función memoizada

  const handleSort = (column) => {
    if (column === sortColumn) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortColumn(column);
      setSortDirection("asc");
    }
  };

  const sortedTransfers = [...transfers].sort((a, b) => {
    if (!a || !b) return 0;
    if (sortColumn === "amount") {
      return sortDirection === "asc"
        ? (a.amount || 0) - (b.amount || 0)
        : (b.amount || 0) - (a.amount || 0);
    } else if (sortColumn === "status") {
      const statusPriority = { completada: 1, pendiente: 2, fallida: 3, default: 4 };
      const prioA = statusPriority[a.status] || statusPriority.default;
      const prioB = statusPriority[b.status] || statusPriority.default;
      if (prioA !== prioB) {
        return sortDirection === "asc" ? prioA - prioB : prioB - prioA;
      }
      // Si el estado es el mismo, ordenar por fecha descendente como secundario
      return new Date(b.timestamp || 0) - new Date(a.timestamp || 0);
    } else if (sortColumn === "is_anomalous") {
      const anomalousA = a.is_anomalous ? 1 : 0;
      const anomalousB = b.is_anomalous ? 1 : 0;
      if (anomalousA !== anomalousB) {
        // Si es asc, no anómalas (0) primero. Si es desc, anómalas (1) primero.
        return sortDirection === "asc" ? anomalousA - anomalousB : anomalousB - anomalousA;
      }
      // Si la anomalía es la misma, ordenar por fecha descendente como secundario
      return new Date(b.timestamp || 0) - new Date(a.timestamp || 0);
    } else {
      // Ordenar por timestamp (por defecto)
      return sortDirection === "asc"
        ? new Date(a.timestamp || 0) - new Date(b.timestamp || 0)
        : new Date(b.timestamp || 0) - new Date(a.timestamp || 0);
    }
  });

  const rows = sortedTransfers.map((transfer) => ({
    id: transfer.id && typeof transfer.id === "string" ? transfer.id.slice(0, 8) : "N/A",
    amount: (
      <MDTypography variant="caption" fontWeight="medium">
        {(transfer.amount ?? 0).toLocaleString("es-ES", {
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
        {transfer.from_account || "N/A"}
      </MDTypography>
    ),
    timestamp: (
      <MDTypography variant="caption">
        {transfer.timestamp ? new Date(transfer.timestamp).toLocaleString("es-ES") : "N/A"}
      </MDTypography>
    ),
    status: (
      <MDBox ml={-1}>
        <MDBadge
          badgeContent={
            transfer.status === "completada"
              ? "Completada"
              : transfer.status === "pendiente"
              ? "Pendiente"
              : transfer.status === "fallida"
              ? "Fallida"
              : "Desconocido" // Fallback
          }
          color={
            transfer.status === "completada"
              ? "success"
              : transfer.status === "pendiente"
              ? "warning"
              : transfer.status === "fallida"
              ? "error"
              : "secondary" // Fallback color
          }
          variant="gradient"
          size="sm"
        />
      </MDBox>
    ),
    is_anomalous: (
      <MDBadge
        badgeContent={transfer.is_anomalous === true ? "Sí" : "No"}
        color={transfer.is_anomalous === true ? "error" : "success"}
        variant="gradient"
        size="sm"
      />
    ),
    // No mostrar nada si no hay ID
    action:
      // Verifica que transfer.id existe antes de crear el link
      transfer.id ? (
        <MDTypography
          component="a"
          href={`/transfer-details/${transfer.id}`}
          variant="caption"
          color="info"
          fontWeight="medium"
        >
          Ver Detalles
        </MDTypography>
      ) : null,
  }));

  const columns = [
    { Header: "ID", accessor: "id", align: "left" },
    {
      Header: () => (
        <MDTypography
          variant="caption"
          fontWeight="bold"
          onClick={() => handleSort("amount")}
          sx={{ cursor: "pointer", "&:hover": { color: "info.main" } }}
        >
          {" "}
          MONTO {sortColumn === "amount" ? (sortDirection === "asc" ? "↑" : "↓") : ""}{" "}
        </MDTypography>
      ),
      accessor: "amount",
      align: "left",
    },
    { Header: "Moneda", accessor: "currency", align: "center" },
    { Header: "Origen", accessor: "from_account", align: "left" },
    {
      Header: () => (
        <MDTypography
          variant="caption"
          fontWeight="bold"
          onClick={() => handleSort("timestamp")}
          sx={{ cursor: "pointer", "&:hover": { color: "info.main" } }}
        >
          {" "}
          FECHA {sortColumn === "timestamp" ? (sortDirection === "asc" ? "↑" : "↓") : ""}{" "}
        </MDTypography>
      ),
      accessor: "timestamp",
      align: "center",
    },
    {
      Header: () => (
        <MDTypography
          variant="caption"
          fontWeight="bold"
          onClick={() => handleSort("status")}
          sx={{ cursor: "pointer", "&:hover": { color: "info.main" } }}
        >
          {" "}
          ESTADO {sortColumn === "status" ? (sortDirection === "asc" ? "↑" : "↓") : ""}{" "}
        </MDTypography>
      ),
      accessor: "status",
      align: "center",
    },
    {
      Header: () => (
        <MDTypography
          variant="caption"
          fontWeight="bold"
          onClick={() => handleSort("is_anomalous")}
          sx={{ cursor: "pointer", "&:hover": { color: "info.main" } }}
        >
          {" "}
          ANÓMALA {sortColumn === "is_anomalous" ? (sortDirection === "asc" ? "↑" : "↓") : ""}{" "}
        </MDTypography>
      ),
      accessor: "is_anomalous",
      align: "center",
    },
    { Header: "Acción", accessor: "action", align: "center" },
  ];

  // Devuelve los datos necesarios para el componente Tables
  return {
    columns,
    rows,
    loading, // Devuelve el estado de carga
    error, // Devuelve el estado de error
    fetchFilteredTransfers, // Devuelve la función para que el componente padre la llame
  };
}
