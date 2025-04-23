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

import React, { useEffect, useState, useCallback } from "react"; // Import useCallback
import axios from "axios";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";
import ReportsBarChart from "examples/Charts/BarCharts/ReportsBarChart";
import MDButton from "components/MDButton";
import MDTypography from "components/MDTypography"; // Asegúrate que está importado si lo usas
import MDInput from "components/MDInput";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import dayjs from "dayjs";
import "dayjs/locale/es"; // Import Spanish locale for dayjs
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import CircularProgress from "@mui/material/CircularProgress"; // Para indicar carga

// Lista de bancos (igual que antes)
const BANCOS_ESP = [
  { code: "0049", name: "Santander" },
  { code: "0075", name: "Banco Popular" },
  { code: "0081", name: "Banco Sabadell" },
  { code: "2100", name: "CaixaBank" },
  { code: "0182", name: "BBVA" },
  { code: "1465", name: "ING" },
  { code: "0128", name: "Bankinter" },
  { code: "2038", name: "Bankia (fusionado con CaixaBank)" },
];

// Estado inicial de los filtros
const initialFiltersState = {
  startDate: null,
  endDate: null,
  bankPrefix: "",
  minAmount: "",
  maxAmount: "",
};

function Dashboard() {
  // Estado para los datos principales (ahora vendrán juntos)
  const [dashboardData, setDashboardData] = useState({
    summary: { totalTransactions: 0, totalAnomalies: 0, totalAmount: 0, newSenders: 0 },
    summaryPreviousMonth: { totalTransfers: 0, totalAnomalies: 0, totalAmount: 0 }, // Opcional
    summaryMonthBeforePrevious: { totalTransfers: 0, totalAnomalies: 0, totalAmount: 0 }, // Opcional
    volumeByDay: [],
    anomalousVolumeByDay: [],
    statusDistribution: [],
    amountByMonth: [], // Datos mensuales ahora vienen filtrados
  });
  const [filters, setFilters] = useState(initialFiltersState);
  const [loading, setLoading] = useState(true); // Estado para indicar carga
  const [error, setError] = useState(null); // Estado para errores

  // --- Lógica de Fetching ---
  const fetchDashboardData = useCallback(async (currentFilters) => {
    setLoading(true);
    setError(null);
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
    const apiUrl = `${process.env.REACT_APP_API_URL}/transfers/dashboard-data${
      queryString ? `?${queryString}` : ""
    }`;

    try {
      const response = await axios.get(apiUrl, { headers });

      setDashboardData({
        summary: response.data.summary || {
          totalTransactions: 0,
          totalAnomalies: 0,
          totalAmount: 0,
          newSenders: 0,
        },
        summaryPreviousMonth: response.data.summaryPreviousMonth || {
          totalTransfers: 0,
          totalAnomalies: 0,
          totalAmount: 0,
        },
        summaryMonthBeforePrevious: response.data.summaryMonthBeforePrevious || {
          totalTransfers: 0,
          totalAnomalies: 0,
          totalAmount: 0,
        },
        volumeByDay: response.data.volumeByDay || [],
        anomalousVolumeByDay: response.data.anomalousVolumeByDay || [],
        statusDistribution: response.data.statusDistribution || [],
        amountByMonth: response.data.amountByMonth || [],
      });
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
      // --- INICIO: Bloque catch mejorado ---
      let errorMessage = "Ocurrió un error inesperado al cargar los datos."; // Mensaje por defecto

      if (err.response) {
        // El servidor respondió con un estado fuera del rango 2xx
        console.error("Error Response Status:", err.response.status);
        console.error("Error Response Data:", err.response.data);

        const responseData = err.response.data;

        // Intenta extraer el mensaje de detalle de FastAPI (puede ser string u objeto/array)
        const detail = responseData?.detail;

        if (detail) {
          if (typeof detail === "string") {
            // Si 'detail' es un string simple (ej: HTTPException normal)
            errorMessage = detail;
          } else if (Array.isArray(detail)) {
            // Si 'detail' es un array (típico de errores de validación 422)
            // Extraemos el mensaje del primer error para simplificar
            try {
              errorMessage = detail.map((e) => `${e.loc?.join(".")} - ${e.msg}`).join("; ");
              if (!errorMessage) {
                // Fallback si el mapeo falla
                errorMessage = JSON.stringify(detail);
              }
            } catch (parseError) {
              console.error("Error parsing validation detail:", parseError);
              errorMessage = JSON.stringify(detail); // Muestra el JSON si falla el parseo
            }
          } else if (typeof detail === "object") {
            // Si 'detail' es un objeto (menos común, pero posible)
            errorMessage = JSON.stringify(detail);
          }
        } else if (typeof responseData === "string") {
          // Si no hay 'detail' pero la respuesta es un string
          errorMessage = responseData;
        } else {
          // Si no se puede extraer un mensaje claro, muestra el status
          errorMessage = `Error del servidor: ${err.response.status}`;
        }
      } else if (err.request) {
        // La petición se hizo pero no se recibió respuesta
        console.error("Error Request:", err.request);
        errorMessage =
          "No se pudo conectar con el servidor. Verifica tu conexión o el estado del servidor.";
      } else {
        // Algo pasó al configurar la petición que lanzó un Error
        console.error("Error Message:", err.message);
        errorMessage = err.message || "Ocurrió un error en la configuración de la petición.";
      }

      setError(errorMessage); // Asegura que 'error' siempre sea un string
      // --- FIN: Bloque catch mejorado ---

      // Opcional: Resetear datos a estado inicial en caso de error
      setDashboardData({
        summary: { totalTransactions: 0, totalAnomalies: 0, totalAmount: 0, newSenders: 0 },
        summaryPreviousMonth: { totalTransfers: 0, totalAnomalies: 0, totalAmount: 0 },
        summaryMonthBeforePrevious: { totalTransfers: 0, totalAnomalies: 0, totalAmount: 0 },
        volumeByDay: [],
        anomalousVolumeByDay: [],
        statusDistribution: [],
        amountByMonth: [],
      });
    } finally {
      setLoading(false);
    }
  }, []); // useCallback para evitar recrear la función en cada render

  // Carga inicial de datos globales (sin filtros)
  useEffect(() => {
    fetchDashboardData(initialFiltersState);
  }, [fetchDashboardData]); // Dependencia de useCallback

  // --- Manejadores de Filtros ---

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    // Permitir solo números (o vacío) para montos
    if (name === "minAmount" || name === "maxAmount") {
      if (value === "" || /^[0-9]*\.?[0-9]*$/.test(value)) {
        setFilters((prevFilters) => ({ ...prevFilters, [name]: value }));
      }
    } else {
      setFilters((prevFilters) => ({ ...prevFilters, [name]: value }));
    }
  };

  const handleBankChange = (event) => {
    setFilters((prevFilters) => ({ ...prevFilters, bankPrefix: event.target.value }));
  };

  const handleDateChange = (name, date) => {
    // Asegurarse que 'date' es un objeto Dayjs válido o null
    setFilters((prevFilters) => ({ ...prevFilters, [name]: date ? dayjs(date) : null }));
  };

  // Función para aplicar los filtros seleccionados
  const applyFilters = () => {
    // Validaciones opcionales (ej: fecha inicio <= fecha fin)
    if (
      filters.startDate &&
      filters.endDate &&
      dayjs(filters.startDate).isAfter(dayjs(filters.endDate))
    ) {
      alert("La fecha de inicio no puede ser posterior a la fecha de fin.");
      return;
    }
    fetchDashboardData(filters);
  };

  // Función para limpiar los campos de filtro
  const clearFilterInputs = () => {
    setFilters(initialFiltersState);
    // No recarga datos automáticamente, solo limpia inputs.
  };

  // Función para restablecer a la vista global
  const restoreGlobalData = () => {
    setFilters(initialFiltersState); // Limpia los inputs también
    fetchDashboardData(initialFiltersState); // Llama a la API sin filtros
  };

  const currentYear = dayjs().year();
  const allMonthsLabels = [
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
  ];
  const monthlyAmountsData = allMonthsLabels.map((label, index) => {
    const monthIndex = index + 1;
    const monthData = dashboardData.amountByMonth.find(
      (item) => item.year === currentYear && item.month === monthIndex
    );
    return monthData ? monthData.amount : 0; // Devuelve el monto o 0 si no hay datos para ese mes
  });

  const reportsAmountChartData = {
    labels: allMonthsLabels,
    datasets: {
      label: "Monto (€)",
      data: monthlyAmountsData,
      fill: true,
      tension: 0.4,
    },
  };

  // Gráfico Volumen por Día
  const reportsVolumeByDayChartData = {
    labels: dashboardData.volumeByDay.map((item) => item.date), // Asume formato YYYY-MM-DD
    datasets: {
      label: "Transferencias",
      data: dashboardData.volumeByDay.map((item) => item.count),
    },
  };

  // Gráfico Volumen Anomalías por Día
  const reportsVolumeAByDayChartData = {
    labels: dashboardData.anomalousVolumeByDay.map((item) => item.date),
    datasets: {
      label: "Anomalías",
      data: dashboardData.anomalousVolumeByDay.map((item) => item.count),
    },
  };

  // Gráfico Distribución de Estados
  const reportsStatusChartData = {
    labels: dashboardData.statusDistribution.map((item) => item.status || "Desconocido"),
    datasets: {
      data: dashboardData.statusDistribution.map((item) => item.count),
      label: "Distribución de Estados", // Título más corto
    },
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      {/* --- Sección de Filtros --- */}
      <MDBox mt={4} mb={2} p={2} sx={{ border: "1px solid #ddd", borderRadius: "8px" }}>
        <MDTypography variant="h6" gutterBottom>
          Filtros
        </MDTypography>
        <Grid container spacing={3} alignItems="center">
          {/* Fila 1: Banco y Montos */}
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel id="bank-prefix-label">Banco</InputLabel>
              <Select
                labelId="bank-prefix-label"
                value={filters.bankPrefix}
                label="Banco"
                name="bankPrefix" // Añadir name para consistencia si se usa en handleInputChange general
                onChange={handleBankChange}
              >
                {/* Opción para "Todos" */}
                <MenuItem value="">
                  <em>Todos</em>
                </MenuItem>
                {BANCOS_ESP.map((bank) => (
                  <MenuItem key={bank.code} value={bank.code}>
                    {bank.name} ({bank.code}) {/* Mostrar código ayuda */}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MDInput
              label="Monto mínimo (€)"
              value={filters.minAmount}
              onChange={handleInputChange}
              name="minAmount"
              type="text" // Usar text para permitir . pero validar con regex
              inputMode="decimal" // Ayuda en móviles
              fullWidth
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MDInput
              label="Monto máximo (€)"
              value={filters.maxAmount}
              onChange={handleInputChange}
              name="maxAmount"
              type="text"
              inputMode="decimal"
              fullWidth
            />
          </Grid>

          {/* Fila 2: Fechas */}
          <Grid item xs={12} sm={6} md={3}>
            <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="es">
              <DatePicker
                label="Fecha de inicio"
                value={filters.startDate}
                onChange={(date) => handleDateChange("startDate", date)}
                format="DD/MM/YYYY"
                slots={{ textField: MDInput }}
                slotProps={{
                  textField: {
                    fullWidth: true,
                  },
                }}
              />
            </LocalizationProvider>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="es">
              <DatePicker
                label="Fecha de fin"
                value={filters.endDate}
                onChange={(date) => handleDateChange("endDate", date)}
                minDate={filters.startDate || undefined}
                format="DD/MM/YYYY"
                slots={{ textField: MDInput }}
                slotProps={{
                  textField: {
                    fullWidth: true,
                  },
                }}
              />
            </LocalizationProvider>
          </Grid>

          {/* Fila 3: Botones */}
          <Grid item xs={12} display="flex" justifyContent="flex-end" gap={1} mt={2}>
            <MDButton variant="gradient" color="info" onClick={applyFilters} disabled={loading}>
              Aplicar Filtros
            </MDButton>
            <MDButton
              variant="outlined"
              color="secondary"
              onClick={clearFilterInputs}
              disabled={loading}
            >
              Limpiar Filtros
            </MDButton>
            <MDButton
              variant="outlined"
              color="warning"
              onClick={restoreGlobalData}
              disabled={loading}
            >
              Restablecer Valores
            </MDButton>
          </Grid>
        </Grid>
      </MDBox>
      {/* --- Sección de Estadísticas y Gráficos --- */}
      {loading ? (
        <MDBox display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </MDBox>
      ) : error ? (
        <MDBox p={3} textAlign="center">
          <MDTypography color="error">Error: {error}</MDTypography>
          <MDButton onClick={() => fetchDashboardData(initialFiltersState)} sx={{ mt: 2 }}>
            Reintentar Carga Global
          </MDButton>
        </MDBox>
      ) : (
        <MDBox py={3}>
          {/* Tarjetas de Estadísticas */}
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} lg={3}>
              <MDBox mb={1.5}>
                <ComplexStatisticsCard
                  color="dark"
                  icon="sync_alt"
                  title="Transferencias"
                  count={dashboardData.summary.totalTransactions}
                  percentage={null}
                />
              </MDBox>
            </Grid>
            <Grid item xs={12} md={6} lg={3}>
              <MDBox mb={1.5}>
                <ComplexStatisticsCard
                  icon="warning"
                  color="error"
                  title="Anomalías detectadas"
                  count={dashboardData.summary.totalAnomalies}
                  percentage={null}
                />
              </MDBox>
            </Grid>
            <Grid item xs={12} md={6} lg={3}>
              <MDBox mb={1.5}>
                <ComplexStatisticsCard
                  color="success"
                  icon="euro_symbol"
                  title="Monto total transferido"
                  count={`${dashboardData.summary.totalAmount.toLocaleString("es-ES", {
                    style: "currency",
                    currency: "EUR",
                  })}`}
                  percentage={null}
                />
              </MDBox>
            </Grid>
            <Grid item xs={12} md={6} lg={3}>
              <MDBox mb={1.5}>
                <ComplexStatisticsCard
                  color="info"
                  icon="people_alt"
                  title="Remitentes Únicos"
                  count={dashboardData.summary.newSenders}
                  percentage={null}
                />
              </MDBox>
            </Grid>
          </Grid>

          {/* Gráficos */}
          <MDBox mt={5}>
            <Grid container spacing={3}>
              {/* Gráfico Volumen Transferencias */}
              <Grid item xs={12} md={6}>
                <MDBox mb={3}>
                  <ReportsLineChart
                    color="info"
                    title="Volumen de Transferencias"
                    description="Transferencias por día en el periodo"
                    date="Datos filtrados"
                    chart={reportsVolumeByDayChartData} // Usa los datos procesados
                  />
                </MDBox>
              </Grid>
              {/* Gráfico Volumen Anomalías */}
              <Grid item xs={12} md={6}>
                <MDBox mb={3}>
                  <ReportsBarChart // Cambiado a Line para consistencia si prefieres
                    color="error" // Color error
                    title="Volumen de Anomalías"
                    description="Anomalías por día en el periodo"
                    date="Datos filtrados"
                    chart={reportsVolumeAByDayChartData} // Usa datos procesados
                  />
                </MDBox>
              </Grid>
            </Grid>

            <Grid container spacing={3} mt={1}>
              {" "}
              {/* Añadido margen superior */}
              {/* Gráfico Distribución Estados */}
              <Grid item xs={12} md={6}>
                <MDBox mb={3}>
                  <ReportsBarChart
                    color="secondary" // Color diferente
                    title="Distribución de Estados"
                    description="Conteo de transferencias por estado final"
                    date="Datos filtrados"
                    chart={reportsStatusChartData}
                  />
                </MDBox>
              </Grid>
              {/* Gráfico Montos Mensuales */}
              <Grid item xs={12} md={6}>
                <MDBox mb={3}>
                  <ReportsLineChart
                    color="success" // Color success para dinero
                    title="Monto Total por Mes"
                    description={`Monto transferido cada mes (${currentYear})`} // Indicar el año
                    date="Datos filtrados"
                    chart={reportsAmountChartData} // Usa los datos mensuales procesados
                  />
                </MDBox>
              </Grid>
            </Grid>
          </MDBox>
        </MDBox>
      )}{" "}
      {/* Fin del bloque condicional loading/error */}
      <Footer />
    </DashboardLayout>
  );
}

export default Dashboard;
