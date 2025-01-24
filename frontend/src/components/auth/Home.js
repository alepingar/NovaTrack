import React, { useEffect, useState } from "react";
import {
  LineChart, Line, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { Layout, Typography, Row, Col, Card } from "antd";
import axios from "axios";

const { Header, Content } = Layout;
const { Title, Text } = Typography;

const HomeDashboard = () => {
  const [summary, setSummary] = useState({
    totalTransactions: 0,
    totalAnomalies: 0,
    totalAmount: 0,
  });
  const [volumeByDay, setVolumeByDay] = useState([]);
  const [amountByCategory, setAmountByCategory] = useState([]);
  const [statusDistribution, setStatusDistribution] = useState([]);
  const [topOriginLocations, setTopOriginLocations] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("token");
      const headers = { Authorization: `Bearer ${token}` };

      // Resumen general
      const summaryRes = await axios.get("http://127.0.0.1:8000/transfers/summary-data", { headers });
      setSummary(summaryRes.data);

      // Datos para los gráficos
      const volumeRes = await axios.get("http://127.0.0.1:8000/transfers/volume-by-day", { headers });
      const categoryRes = await axios.get("http://127.0.0.1:8000/transfers/amount-by-category", { headers });
      const statusRes = await axios.get("http://127.0.0.1:8000/transfers/status-distribution", { headers });
      const locationRes = await axios.get("http://127.0.0.1:8000/transfers/top-origin-locations", { headers });

      setVolumeByDay(volumeRes.data);
      setAmountByCategory(categoryRes.data);
      setStatusDistribution(statusRes.data);
      setTopOriginLocations(locationRes.data);
    };

    fetchData();
  }, []);

  return (
    <Layout>
      <Header style={{ background: "#001529", padding: "0 20px" }}>
        <Title level={3} style={{ color: "#fff", margin: 0 }}>
          Dashboard de Transferencias
        </Title>
      </Header>
      <Content style={{ margin: "20px" }}>
        {/* Tarjetas de resumen */}
        <Row gutter={[16, 16]}>
          <Col span={8}>
            <Card>
              <Title level={4}>Transacciones Totales</Title>
              <Text style={{ fontSize: "20px", fontWeight: "bold" }}>
                {summary.totalTransactions}
              </Text>
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Title level={4}>Anomalías Detectadas</Title>
              <Text style={{ fontSize: "20px", fontWeight: "bold" }}>
                {summary.totalAnomalies}
              </Text>
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Title level={4}>Monto Total Transferido</Title>
              <Text style={{ fontSize: "20px", fontWeight: "bold" }}>
                ${summary.totalAmount.toLocaleString("es-ES")}
              </Text>
            </Card>
          </Col>
        </Row>

        {/* Gráficos */}
        <Row gutter={[16, 16]} style={{ marginTop: "20px" }}>
          <Col span={12}>
            <Card title="Volumen de Transacciones por Día">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={volumeByDay}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="count" stroke="#8884d8" />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="Distribución de Montos por Categoría">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={amountByCategory} dataKey="amount" nameKey="category" cx="50%" cy="50%" outerRadius={100}>
                    {amountByCategory.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={`hsl(${index * 40}, 70%, 50%)`} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </Col>
        </Row>

        <Row gutter={[16, 16]} style={{ marginTop: "20px" }}>
          <Col span={12}>
            <Card title="Distribución del Estado de las Transacciones">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={statusDistribution} dataKey="count" nameKey="status" cx="50%" cy="50%" outerRadius={100}>
                    {statusDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={`hsl(${index * 40}, 70%, 50%)`} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="Ubicaciones de Origen Más Comunes">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={topOriginLocations}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="location" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </Col>
        </Row>
      </Content>
    </Layout>
  );
};

export default HomeDashboard;
