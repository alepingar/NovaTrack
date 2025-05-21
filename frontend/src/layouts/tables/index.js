// En layouts/tables/index.js

import React, { useState, useCallback } from "react"; // Import useCallback
// Imports de Material UI y componentes MD (Grid, Card, MDBox, MDTypography, etc.)
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import DataTable from "examples/Tables/DataTable";
import useTransfersTableData from "layouts/tables/data/transfersTableData";
import MDButton from "components/MDButton";
import { Snackbar, Alert, CircularProgress } from "@mui/material";
import MDInput from "components/MDInput";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import dayjs from "dayjs";
import "dayjs/locale/es";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";

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

// Estado inicial para los nuevos filtros
const initialFiltersState = {
  startDate: null,
  endDate: null,
  bankPrefix: "",
  minAmount: "",
  maxAmount: "",
};

function Tables() {
  // Estado para los filtros detallados
  const [filters, setFilters] = useState(initialFiltersState);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState("success");

  // Usa el hook refactorizado
  const { columns, rows, loading, error, fetchFilteredTransfers } = useTransfersTableData();

  const handleInputChange = (event) => {
    const { name, value } = event.target;
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
    setFilters((prevFilters) => ({ ...prevFilters, [name]: date ? dayjs(date) : null }));
  };

  // --- Funciones de Botones de Filtro ---
  const applyTableFilters = useCallback(() => {
    if (
      filters.startDate &&
      filters.endDate &&
      dayjs(filters.startDate).isAfter(dayjs(filters.endDate))
    ) {
      setSnackbarMessage("Error: La fecha de inicio no puede ser posterior a la fecha de fin.");
      setSnackbarSeverity("error");
      setSnackbarOpen(true);
      return;
    }
    // Llama a la función de fetch del hook con los filtros actuales
    fetchFilteredTransfers(filters);
    setSnackbarMessage("Filtros aplicados a la tabla.");
    setSnackbarSeverity("success");
    setSnackbarOpen(true);
  }, [filters, fetchFilteredTransfers]);

  const clearTableFilterInputs = () => {
    setFilters(initialFiltersState);
    // Solo limpia los inputs, no recarga datos
  };

  const restoreTableDefaults = useCallback(() => {
    setFilters(initialFiltersState); // Limpia inputs
    fetchFilteredTransfers({}); // Llama a fetch sin filtros para obtener todos
    setSnackbarMessage("Mostrando todas las transferencias.");
    setSnackbarSeverity("info");
    setSnackbarOpen(true);
  }, [fetchFilteredTransfers]); // Depende solo de la función de fetch

  const handleSnackbarClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setSnackbarOpen(false);
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox
        pt={6}
        pb={3}
        sx={{
          display: "flex",
          flexDirection: "column",
          flexGrow: 1,
          minHeight: "calc(100vh - 64px)",
        }}
      >
        <Grid container spacing={6}>
          <Grid item xs={12}>
            <Card>
              <MDBox
                mx={2}
                mt={-3}
                py={3}
                px={2}
                variant="gradient"
                bgColor="info"
                borderRadius="lg"
                coloredShadow="info"
              >
                <MDTypography variant="h6" color="white">
                  Tabla de Transferencias
                </MDTypography>
              </MDBox>

              {/* --- Sección de Filtros (Similar al Dashboard) --- */}
              <MDBox mt={2} mb={1} p={2}>
                <Grid container spacing={2} alignItems="center">
                  {/* Fila 1: Banco y Montos */}
                  <Grid item xs={12} sm={6} md={3}>
                    <FormControl fullWidth variant="outlined" size="small">
                      <InputLabel id="table-bank-prefix-label">Banco</InputLabel>
                      <Select
                        labelId="table-bank-prefix-label"
                        value={filters.bankPrefix}
                        label="Banco"
                        name="bankPrefix"
                        onChange={handleBankChange}
                      >
                        <MenuItem value="">
                          <em>Todos</em>
                        </MenuItem>
                        {BANCOS_ESP.map((bank) => (
                          <MenuItem key={bank.code} value={bank.code}>
                            {bank.name} ({bank.code})
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6} md={2}>
                    <MDInput
                      label="Monto mín (€)"
                      value={filters.minAmount}
                      onChange={handleInputChange}
                      name="minAmount"
                      type="text"
                      inputMode="decimal"
                      fullWidth
                      variant="outlined"
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={2}>
                    <MDInput
                      label="Monto máx (€)"
                      value={filters.maxAmount}
                      onChange={handleInputChange}
                      name="maxAmount"
                      type="text"
                      inputMode="decimal"
                      fullWidth
                      variant="outlined"
                      size="small"
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
                          textField: { fullWidth: true, variant: "outlined", size: "small" },
                        }}
                      />
                    </LocalizationProvider>
                  </Grid>
                  <Grid item xs={12} sm={6} md={2}>
                    <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="es">
                      <DatePicker
                        label="Fecha de fin"
                        value={filters.endDate}
                        onChange={(date) => handleDateChange("endDate", date)}
                        minDate={filters.startDate || undefined}
                        format="DD/MM/YYYY"
                        slots={{ textField: MDInput }}
                        slotProps={{
                          textField: { fullWidth: true, variant: "outlined", size: "small" },
                        }}
                      />
                    </LocalizationProvider>
                  </Grid>

                  {/* Fila 3: Botones */}
                  <Grid item xs={12} display="flex" justifyContent="flex-start" gap={1}>
                    <MDButton
                      variant="gradient"
                      color="info"
                      onClick={applyTableFilters}
                      disabled={loading}
                      size="small"
                    >
                      Aplicar Filtros
                    </MDButton>
                    <MDButton
                      variant="outlined"
                      color="secondary"
                      onClick={clearTableFilterInputs}
                      disabled={loading}
                      size="small"
                    >
                      Limpiar
                    </MDButton>
                    <MDButton
                      variant="outlined"
                      color="warning"
                      onClick={restoreTableDefaults}
                      disabled={loading}
                      size="small"
                    >
                      Mostrar Todos
                    </MDButton>
                  </Grid>
                </Grid>
              </MDBox>

              {loading && (
                <MDBox display="flex" justifyContent="center" p={3}>
                  <CircularProgress color="info" />
                </MDBox>
              )}
              {error && !loading && (
                <MDBox p={2}>
                  <Alert severity="error">Error al cargar datos: {error}</Alert>
                </MDBox>
              )}

              {!loading && !error && (
                <MDBox pt={1}>
                  {" "}
                  <DataTable
                    table={{ columns, rows }}
                    isSorted={false} // La ordenación se hace en el hook
                    entriesPerPage={{ defaultValue: 10, entries: [5, 10, 20, 50] }} // Opciones de paginación
                    showTotalEntries={true} // Muestra el total
                    pagination={{ variant: "gradient", color: "info" }} // Estilo de paginación
                    canSearch={true} // Habilita búsqueda (filtra client-side los datos actuales)
                    noEndBorder
                  />
                </MDBox>
              )}
            </Card>
          </Grid>
        </Grid>
      </MDBox>
      <Footer />
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000} // Un poco más de duración
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbarSeverity}
          sx={{ width: "100%" }}
          variant="filled"
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </DashboardLayout>
  );
}

export default Tables;
