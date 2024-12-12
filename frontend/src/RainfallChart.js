import React, { useState, useEffect, useRef } from "react";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";

// Chart.js の登録
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function RainfallChart() {
    const [rainfallData, setRainfallData] = useState([]);
    const [labels, setLabels] = useState([]);

    useEffect(() => {
        const fetchRainfallData = async () => {
            const response = await fetch("http://localhost:5000/api/rainfall");
            const data = await response.json();

            setLabels(data.map((item) => item.time));
            setRainfallData(data.map((item) => item.rainfall));
        };

        fetchRainfallData();
    }, []);

    const chartData = {
        labels: labels,
        datasets: [
            {
                label: "降水量 (mm)",
                data: rainfallData,
                backgroundColor: "rgba(75, 192, 192, 0.6)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1,
            },
        ],
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: "降水量 (mm)",
                },
            },
            x: {
                title: {
                    display: true,
                    text: "時間",
                },
            },
        },
    };

    return <Bar data={chartData} options={chartOptions} />;
}

export default RainfallChart;
