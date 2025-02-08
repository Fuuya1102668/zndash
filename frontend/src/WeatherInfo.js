import React, { useState, useEffect } from "react";
import axios from "axios";

function WeatherInfo() {
    const [todayWeather, setTodayWeather] = useState("");
    const [tomorrowWeather, setTomorrowWeather] = useState("");
    const [highTemp, setHighTemp] = useState(null);
    const [lowTemp, setLowTemp] = useState(null);
    const [rainProbability, setRainProbability] = useState(null);

    useEffect(() => {
        const fetchWeatherData = async () => {
            try {
                const response = await axios.get("http://202.13.169.105:5000/api/weather");
                const data = response.data;

                // データをstateにセット
                setTodayWeather(data.todayWeather || "不明");
                setTomorrowWeather(data.tomorrowWeather || "不明");
                setHighTemp(data.highTemp || "N/A");
                setLowTemp(data.lowTemp || "N/A");
                setRainProbability(data.rainProbability || "N/A");
            } catch (error) {
                console.error("Failed to fetch weather data:", error);
            }
        };

        fetchWeatherData();
    }, []);

    return ();
}

export default WeatherInfo;
