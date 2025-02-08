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

    // 1~4 の間で 0.01 刻みのランダムな増加量を生成する関数
    const getRandomIncrease = () => {
        return parseFloat((Math.random() * (4 - 1) + 1).toFixed(2));
    };

    useEffect(() => {
        const fetchRainfallData = async () => {
            const response = await fetch("http://202.13.169.105:5000/api/rainfall");
            const data = await response.json();

            // データを加工してランダムな増加量を追加
            //const adjustedRainfall = data.map((item) => ({
            //    ...item,
            //    rainfall: item.rainfall + getRandomIncrease(), // ランダムな増加量を追加
            //}));

            //setLabels(adjustedRainfall.map((item) => item.time.slice(-4)));
            //setRainfallData(adjustedRainfall.map((item) => item.rainfall));

            setLabels(data.map((item) => item.time.slice(-4)));
            setRainfallData(data.map((item) => item.rainfall));
        };

        fetchRainfallData();

        // 5分ごとにデータを取得
        const interval = setInterval(fetchRainfallData, 300000);
    
        return () => clearInterval(interval);
    }, []);

    const chartData = {
        labels: labels,
        datasets: [
            {
                label: "",
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
        plugins: {
            legend: {
                display: false,
            },
            title: {
                display: false, // タイトルを非表示
            },
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 5.0,
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
