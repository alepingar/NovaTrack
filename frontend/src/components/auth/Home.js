import React, { useEffect, useState } from "react";
import axios from "axios";
import {
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    Legend,
} from "recharts";
import "../../css/styles.css";

function Home() {
    const [data, setData] = useState({
        topUsers: [],
        anomalyDistribution: [],
        dailyTransactions: [],
    });

    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const token = localStorage.getItem("token");
                const response = await axios.get("http://127.0.0.1:8000/dashboard", {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                setData(response.data);
                setLoading(false);
            } catch (error) {
                console.error("Error fetching dashboard data:", error);
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) {
        return <div className="text-center">Cargando...</div>;
    }

    const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

    return (
        <div className="container mt-5">
            <div className="row">
                <div className="col-md-6 mb-4">
                    <div className="card shadow-sm">
                        <div className="card-header bg-primary text-white">
                            <h5>Usuarios con más transferencias</h5>
                        </div>
                        <div className="card-body">
                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart data={data.topUsers}>
                                    <XAxis dataKey="user" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="transactions" fill="#8884d8" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                <div className="col-md-6 mb-4">
                    <div className="card shadow-sm">
                        <div className="card-header bg-primary text-white">
                            <h5>Distribución de anomalías</h5>
                        </div>
                        <div className="card-body">
                            <ResponsiveContainer width="100%" height={300}>
                                <PieChart>
                                    <Pie
                                        data={data.anomalyDistribution}
                                        dataKey="value"
                                        nameKey="type"
                                        cx="50%"
                                        cy="50%"
                                        outerRadius={100}
                                        fill="#8884d8"
                                        label
                                    >
                                        {data.anomalyDistribution.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                    <Legend />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>
            </div>

            <div className="row">
                <div className="col-md-12">
                    <div className="card shadow-sm">
                        <div className="card-header bg-primary text-white">
                            <h5>Transacciones Diarias</h5>
                        </div>
                        <div className="card-body">
                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart data={data.dailyTransactions}>
                                    <XAxis dataKey="date" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="transactions" fill="#82ca9d" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Home;
