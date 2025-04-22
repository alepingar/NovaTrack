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

import React, { useEffect, useState } from "react";
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
import MDTypography from "components/MDTypography";
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

function Dashboard() {
  const [summary, setSummary] = useState({
    totalTransactions: 0,
    totalAnomalies: 0,
    totalAmount: 0,
  });

  const today = new Date();
  const currentYear = today.getFullYear();
  const currentMonth = today.getMonth() + 1;
  const previousMonth = currentMonth === 1 ? 12 : currentMonth - 1;
  const previousYear = currentMonth === 1 ? currentYear - 1 : currentYear;

  const [summaryP, setSummaryP] = useState({
    totalTransfers: 0,
    totalAnomalies: 0,
    totalAmount: 0,
  });
  const [summaryPA, setSummaryPA] = useState({
    totalTransfers: 0,
    totalAnomalies: 0,
    totalAmount: 0,
  });
  const [volumeByDay, setVolumeByDay] = useState([]);
  const [volumeAByDay, setVolumeAByDay] = useState([]);
  const [statusDistribution, setStatusDistribution] = useState([]);
  const [newSenders, setNewSenders] = useState(0);
  const [amount, setAmount] = useState([]);
  const [filterPeriod, setFilterPeriod] = useState("3months");

  const [filters, setFilters] = useState({
    startDate: null,
    endDate: null,
    bankPrefix: "",
    minAmount: "",
    maxAmount: "",
  });

  const fetchDashboardData = async (currentFilters) => {
    const token = localStorage.getItem("token");
    const headers = { Authorization: `Bearer ${token}` };
    const queryParams = new URLSearchParams();

    if (currentFilters.startDate)
      queryParams.append("start_date", currentFilters.startDate.toISOString());
    if (currentFilters.endDate)
      queryParams.append("end_date", currentFilters.endDate.toISOString());
    if (currentFilters.bankPrefix && currentFilters.bankPrefix.trim() !== "")
      queryParams.append("bank_prefix", currentFilters.bankPrefix.trim());
    if (currentFilters.minAmount && currentFilters.minAmount.trim() !== "")
      queryParams.append("min_amount", currentFilters.minAmount.trim());
    if (currentFilters.maxAmount && currentFilters.maxAmount.trim() !== "")
      queryParams.append("max_amount", currentFilters.maxAmount.trim());

    const queryString = queryParams.toString();

    try {
      const summaryRes = await axios.get(
        `${process.env.REACT_APP_API_URL}/transfers/summary-data${
          queryString ? `?${queryString}` : ""
        }`,
        { headers }
      );
      setSummary(summaryRes.data);

      const summaryPRes = await axios.get(
        `${process.env.REACT_APP_API_URL}/transfers/summary/per-month/${currentYear}/${currentMonth}`,
        { headers }
      );
      setSummaryP(summaryPRes.data);

      const summaryPARes = await axios.get(
        `${process.env.REACT_APP_API_URL}/transfers/summary/per-month/${previousYear}/${previousMonth}`,
        { headers }
      );
      setSummaryPA(summaryPARes.data);

      const volumeRes = await axios.get(
        `${process.env.REACT_APP_API_URL}/transfers/volume-by-day${
          queryString ? `?${queryString}` : ""
        }`,
        { headers }
      );
      setVolumeByDay(volumeRes.data);

      const volumeARes = await axios.get(
        `${process.env.REACT_APP_API_URL}/transfers/anomalous/volume-by-day${
          queryString ? `?${queryString}` : ""
        }`,
        { headers }
      );
      setVolumeAByDay(volumeARes.data);

      const statusRes = await axios.get(
        `${process.env.REACT_APP_API_URL}/transfers/status-distribution${
          queryString ? `?${queryString}` : ""
        }`,
        { headers }
      );
      setStatusDistribution(statusRes.data);

      const newSendersRes = await axios.get(
        `${process.env.REACT_APP_API_URL}/transfers/new-senders${
          queryString ? `?${queryString}` : ""
        }`,
        { headers }
      );
      setNewSenders(newSendersRes.data);

      const amountPromises = [];
      for (let month = 1; month <= 12; month++) {
        amountPromises.push(
          axios.get(
            `${process.env.REACT_APP_API_URL}/transfers/amount/company/per-month/${currentYear}/${month}`,
            { headers }
          )
        );
      }
      const amountResponses = await Promise.all(amountPromises);
      const amounts = amountResponses.map((response) => response.data);
      setAmount(amounts);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchDashboardData(filters);
  }, []);

  // Cambia la función applyFilters para que se encargue de aplicar los filtros
  const applyFilters = () => {
    fetchDashboardData(filters); // Llamada a la API para obtener los datos con los filtros aplicados
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFilters((prevFilters) => ({ ...prevFilters, [name]: value }));
  };

  const handleBankChange = (event) => {
    setFilters({ ...filters, bankPrefix: event.target.value });
  };

  const handleDateChange = (name, date) => {
    setFilters({ ...filters, [name]: date });
  };

  const clearFilters = () => {
    setFilters({ startDate: null, endDate: null, bankPrefix: "", minAmount: "", maxAmount: "" });
    setFilterPeriod("3months");
  };

  const getFilteredAmountData = (data) => {
    const today = new Date();
    const currentMonth = today.getMonth() + 1;
    if (filterPeriod === "month") {
      return data.slice(0, currentMonth);
    } else if (filterPeriod === "3months") {
      const months = Math.min(12, currentMonth + 2);
      return data.slice(0, months);
    } else {
      return data;
    }
  };

  const reportsAmountChartData = {
    labels:
      amount.length > 0
        ? [
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
          ].slice(0, getFilteredAmountData(amount).length)
        : [],
    datasets: {
      label: "Monto",
      data: getFilteredAmountData(amount),
      fill: true,
      tension: 0.4,
    },
  };

  const reportsVolumeByDayChartData = {
    labels: volumeByDay.map((item) => item.date),
    datasets: {
      label: "Transferencias",
      data: volumeByDay.map((item) => item.count),
    },
  };

  const reportsVolumeAByDayChartData = {
    labels: volumeAByDay.map((item) => item.date),
    datasets: {
      label: "Anomalías",
      data: volumeAByDay.map((item) => item.count),
    },
  };

  const reportsStatusChartData = {
    labels: statusDistribution.map((item) => item.status),
    datasets: {
      data: statusDistribution.map((item) => item.count),
      label: "Distribución del estado de las Transacciones",
    },
  };

  const calculatePercentage = (previous, current) => {
    if (previous === 0) return { amount: current, color: "success" };
    const diff = current - previous;
    const percentage = ((diff / previous) * 100).toFixed(2);
    const isPositive = diff > 0;
    return {
      amount: isPositive ? `+${percentage}%` : `-${Math.abs(percentage)}%`,
      color: isPositive ? "success" : "error",
    };
  };

  const transfersChange = calculatePercentage(summaryPA.totalTransfers, summaryP.totalTransfers);
  const anomalyChange = calculatePercentage(summaryPA.totalAnomalies, summaryP.totalAnomalies);
  const amountChange = calculatePercentage(summaryPA.totalAmount, summaryP.totalAmount);

  return (
    <DashboardLayout>
      <DashboardNavbar />

      {/* Filtros */}
      <MDBox mt={5}>
        <FormControl sx={{ m: 1, minWidth: 120 }}>
          <InputLabel id="bank-prefix-label">Banco</InputLabel>
          <Select
            labelId="bank-prefix-label"
            value={filters.bankPrefix}
            label="Banco"
            onChange={handleBankChange}
          >
            {BANCOS_ESP.map((bank) => (
              <MenuItem key={bank.code} value={bank.code}>
                {bank.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <MDBox display="flex" alignItems="center" gap={2}>
            <MDInput
              label="Monto mínimo"
              value={filters.minAmount}
              onChange={handleInputChange}
              name="minAmount"
            />
            <MDInput
              label="Monto máximo"
              value={filters.maxAmount}
              onChange={handleInputChange}
              name="maxAmount"
            />
            <DatePicker
              label="Fecha de inicio"
              value={filters.startDate}
              onChange={(date) => handleDateChange("startDate", date)}
              renderInput={(params) => <MDInput {...params} />}
            />
            <DatePicker
              label="Fecha de fin"
              value={filters.endDate}
              onChange={(date) => handleDateChange("endDate", date)}
              renderInput={(params) => <MDInput {...params} />}
            />
          </MDBox>
        </LocalizationProvider>

        <MDBox mt={3}>
          <MDButton color="info" onClick={applyFilters}>
            Aplicar filtros
          </MDButton>
          <MDButton color="warning" onClick={clearFilters} sx={{ ml: 2 }}>
            Limpiar filtros
          </MDButton>
        </MDBox>
      </MDBox>
      <MDBox py={3}>
        <Grid container spacing={3}>
          {/* Card: Transferencias Totales */}
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="dark"
                icon="sync_alt"
                title="Transferencias"
                count={summary.totalTransactions}
                percentage={{
                  color: transfersChange.color,
                  amount: transfersChange.amount,
                  label:
                    transfersChange.color === "success" ? "En crecimiento" : "En decrecimiento",
                }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                icon="warning"
                title="Anomalías detectadas"
                count={summary.totalAnomalies}
                percentage={{
                  color: anomalyChange.color,
                  amount: anomalyChange.amount,
                  label: anomalyChange.color === "success" ? "En crecimiento" : "En decrecimiento",
                }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="success"
                icon="attach_money"
                title="Cantitad total transferida"
                count={`${summary.totalAmount.toLocaleString("es-ES")}€`}
                percentage={{
                  color: amountChange.color,
                  amount: amountChange.amount,
                  label: amountChange.color === "success" ? "En crecimiento" : "En decrecimiento",
                }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="primary"
                icon="person"
                title="Nuevos remitentes de este mes"
                count={newSenders | 0}
                percentage={{
                  color: amountChange.color,
                  amount: amountChange.amount,
                  label: amountChange.color === "success" ? "En crecimiento" : "En decrecimiento",
                }}
              />
            </MDBox>
          </Grid>
        </Grid>

        {/* Gráficos */}
        <MDBox mt={5}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={6}>
              <MDBox mb={3} mt={5}>
                <ReportsLineChart
                  color="info"
                  title="Crecimiento de transferencias"
                  description="Cantidad de transferencias analizadas a lo largo del periodo seleccionado"
                  date="Actualización automática"
                  chart={reportsVolumeByDayChartData}
                />
              </MDBox>
            </Grid>

            <Grid item xs={12} sm={6} md={6}>
              <MDBox mb={3} mt={5}>
                <ReportsBarChart
                  color="primary"
                  title="Procesamiento de anomalías"
                  description="Distribución de anomalías en el periodo seleccionado"
                  date="Actualización automática"
                  chart={reportsVolumeAByDayChartData}
                />
              </MDBox>
            </Grid>
          </Grid>

          <Grid container spacing={3}>
            {/* Gráfico de Distribución de Estados */}
            <Grid item xs={12} sm={6} md={6}>
              <MDBox mt={4.5}>
                <ReportsBarChart
                  color="error"
                  title="Distribución de estados de transacción"
                  description="Desglose de los diferentes estados de las transacciones a través del tiempo"
                  date="Actualización automática"
                  chart={reportsStatusChartData}
                />
              </MDBox>
            </Grid>

            {/* Gráfico de Crecimiento de Montos */}
            <Grid item xs={12} sm={6} md={6}>
              <MDBox mt={4.5}>
                <ReportsLineChart
                  color="dark"
                  title="Crecimiento de montos"
                  description="Cantidad de montos analizados a lo largo del periodo seleccionado"
                  date="Actualización automática"
                  chart={reportsAmountChartData}
                />
              </MDBox>
            </Grid>
          </Grid>
        </MDBox>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Dashboard;
