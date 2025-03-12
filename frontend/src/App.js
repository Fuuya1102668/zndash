import React, { useState, useEffect, } from "react";
import RainfallChart from "./RainfallChart";
import axios from "axios";
import "./App.css";

const ipaddr = "202.13.169.105"

function App() {
    const [year, setYear] = useState("");
    const [month, setMonth] = useState("");
    const [day, setDay] = useState("");
    const [time, setTime] = useState("");
    const [itmedia, setItmedia] = useState([]);
    const [zennllm, setzennllm] = useState([]);
    const [huggingface, sethuggingface] = useState([]);
    const [weatherData, setWeatherData] = useState({
        todayWeather: "",
        tomorrowWeather: "",
        maxTemp: "",
        minTemp: "",
        averageRainChance: "",
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const updateDateTime = () => {
            const now = new Date();

            // 日付のフォーマット
            const formattedYear = `${now.getFullYear()}年`;
            const formattedMonth = `${String(now.getMonth() + 1).padStart(2, "0")}月`;
            const formattedDay = `${String(now.getDate()).padStart(2, "0")}日`;

            // 時刻のフォーマット
            const formattedTime = now.toLocaleTimeString("ja-JP", {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
            });

            setYear(formattedYear);
            setMonth(formattedMonth);
            setDay(formattedDay);
            setTime(formattedTime);
        };
        const fetchItmedia = async () => {
            try {
                const response = await fetch('http://202.13.169.105:5000/api/itmedia'); // バックエンドのAPIを呼び出す
                if (!response.ok) {
                    throw new Error('Failed to fetch RSS data');
                }
                const data = await response.json();
                setItmedia(data);
            } catch (error) {
                setError(error.message);
            } finally {
                setLoading(false);
            }
        };
        const fetchzennllm = async () => {
            try {
                const response = await fetch('http://202.13.169.105:5000/api/zennllm'); // バックエンドのAPIを呼び出す
                if (!response.ok) {
                    throw new Error('Failed to fetch RSS data');
                }
                const data = await response.json();
                setzennllm(data);
            } catch (error) {
                setError(error.message);
            } finally {
                setLoading(false);
            }
        };
        const fetchhuggingface = async () => {
            try {
                const response = await fetch('http://202.13.169.105:5000/api/huggingface'); // バックエンドのAPIを呼び出す
                if (!response.ok) {
                    throw new Error('Failed to fetch RSS data');
                }
                const data = await response.json();
                sethuggingface(data);
            } catch (error) {
                setError(error.message);
            } finally {
                setLoading(false);
            }
        };
        const fetchWeatherData = async () => {
            try {
                const response = await axios.get("http://202.13.169.105:5000/api/weather");
                setWeatherData(response.data);
            } catch (err) {
                console.error("Error fetching weather data:", err);
                setError("天気情報を取得できませんでした。");
            }
        };


        // 初回実行
        updateDateTime();
        fetchItmedia();
        fetchzennllm();
        fetchhuggingface();
        fetchWeatherData();

        // 1秒ごとに日付と時刻を更新
        const dateTimerInterval = setInterval(updateDateTime, 1000);
        // 1分ごとにitmediaを取得
        const itmediaInterval = setInterval(fetchItmedia, 60000);
        // 1分ごとにzennのllmを取得
        const zennllmInterval = setInterval(fetchzennllm, 60000);
        // 1分ごとにopenaiを取得
        const huggingfaceInterval = setInterval(fetchhuggingface, 60000);
        // 10分ごとに天気を取得
        const weatherInterval = setInterval(fetchWeatherData, 600000);

        // クリーンアップ
        return () => {
            clearInterval(dateTimerInterval);
            clearInterval(itmediaInterval);
            clearInterval(zennllmInterval);
            clearInterval(huggingfaceInterval);
            clearInterval(weatherInterval);
        };
    }, []);

    return (
        <div className="container">
            <div className="date-time-container">
                <div className="date-section">{year}{month}{day}</div>
                <div className="time-section">{time}</div>
            </div>
            <div className="weather-container">
                <div className="today-section">
                    <div className="rainfallchart">
                        <RainfallChart />
                    </div>
                    <div className="info">
                        {weatherData.todayWeather}
                    </div>
                </div>
                <div className="tomorrow-section">
                    <div className="icon">
                        {weatherData.tomorrowWeather}
                        <img src="/icons/sun.svg" alt="晴れ"/>
                    </div>
                    <div className="max-text">明日の最高気温</div>
                    <div className="max">{weatherData.maxTemp}℃</div>
                    <div className="min-text">明日の最低気温</div>
                    <div className="min">{weatherData.minTemp}℃</div>
                    <div className="rain-chance-text">降水確率</div>
                    <div className="rain-chance">{weatherData.averageRainChance}</div>
                </div>
            </div>
            <div className="itmedia-section">
                {itmedia.map((article, index) => (
                    <div  className="itmedia" key={index}>
                        <strong className="itmedia-title">{article.title}</strong>
                        <p className="itmedia-description">{article.description}</p>
                    </div>
                ))}
            </div>
            <div className="zennllm-section">
                {zennllm.map((article, index) => (
                    <div  className="zennllm" key={index}>
                        <strong className="zennllm-title">{article.title}</strong>
                        <p className="zennllm-description">{article.description}</p>
                    </div>
                ))}
            </div>
            <div className="huggingface-section">
                {huggingface.map((article, index) => (
                    <div  className="huggingface" key={index}>
                        <strong className="huggingface-title">{article.title}</strong>
                        <p className="huggingface-description">{article.description}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default App;
