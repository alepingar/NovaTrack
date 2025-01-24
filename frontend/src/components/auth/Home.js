import React, { useEffect, useState } from "react";
import { Layout, Typography, Row, Col, Card, List } from "antd";
import axios from "axios";

const { Header, Content } = Layout;
const { Title, Text } = Typography;

const HomeDashboard = () => {
  const [summary, setSummary] = useState({
    totalTransactions: 0,
    totalAnomalies: 0,
    totalAmount: 0,
  });
  const [transactions, setTransactions] = useState([]);
  const [anomalies, setAnomalies] = useState([]);

  const fetchSummaryData = async () => {
    try {
      const token = localStorage.getItem("token");
      console.log("Token obtenido:", token);

      // Realiza la solicitud al backend
      const response = await axios.get(
        "http://127.0.0.1:8000/transfers/summary-data",
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      console.log("Respuesta del backend:", response.data);

      // Actualiza el estado con los datos reales
      setSummary(response.data);
    } catch (error) {
      console.error("Error al obtener el resumen:", error.response || error.message);
    }
  };

  useEffect(() => {
    fetchSummaryData();
  }, []);

  return (
    <Layout>
      <Header style={{ background: "#001529", padding: "0 20px" }}>
        <Title level={3} style={{ color: "#fff", margin: 0 }}>
          Dashboard de Transferencias
        </Title>
      </Header>
      <Content style={{ margin: "20px" }}>
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

        <Row gutter={[16, 16]} style={{ marginTop: "20px" }}>
          <Col span={12}>
            <Card title="Últimas Transacciones">
              <List
                dataSource={transactions}
                renderItem={(transaction) => (
                  <List.Item>
                    Fecha: {transaction.date}, Monto: ${transaction.amount}
                  </List.Item>
                )}
              />
            </Card>
          </Col>
          <Col span={12}>
            <Card title="Anomalías Detectadas">
              <List
                dataSource={anomalies}
                renderItem={(anomaly) => (
                  <List.Item>
                    {anomaly.description} - {anomaly.date}
                  </List.Item>
                )}
              />
            </Card>
          </Col>
        </Row>
      </Content>
    </Layout>
  );
};

export default HomeDashboard;
