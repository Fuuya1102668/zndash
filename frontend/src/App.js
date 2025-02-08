//import React, { useState, useEffect } from "react";
//import { Canvas } from "@react-three/fiber";
//import { OrbitControls, useGLTF } from "@react-three/drei";
//import "./App.css";

import React, { useState, useEffect, useRef, } from "react";
import RainfallChart from "./RainfallChart";
import { Bar } from "react-chartjs-2";
import axios from "axios";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";
import { FBXLoader } from "three/examples/jsm/loaders/FBXLoader";
import "./App.css";

//function ZndModel() {
//     const { scene } = useGLTF("/models/znd-model.glb"); // 3Dモデルのパス
//     return <primitive object={scene} scale={2} />;
//}

const ipaddr = "202.13.169.105"
function ZndModel() {
    const modelRef = useRef();
    const mixerRef = useRef();
  
    useEffect(() => {
        const loader = new FBXLoader();
        loader.load(
            "/models/znd-model_tex.fbx", // FBXファイルのパス
            (object) => {
                object.scale.set(0.05, 0.05, 0.05); // サイズ調整
                object.position.set(0, -2.5, -4); // モデル全体を下に移動
                modelRef.current.add(object);
                modelRef.current.rotation.x -= 0.5; // モデルの回転 
                // アニメーションのセットアップ
                if (object.animations.length > 0) {
                    const mixer = new THREE.AnimationMixer(object);
                    const action = mixer.clipAction(object.animations[0]); // 最初のアニメーションを再生
                    action.play();
                    mixerRef.current = mixer;
                }
            },
            undefined,
            (error) => {
                console.error("Error loading FBX model:", error);
            }
        );
    }, []);
    useFrame((_, delta) => {
        if (mixerRef.current) {
            mixerRef.current.update(delta); // 毎フレームの更新
        }
    });
  
    return <group ref={modelRef} />;
}

function App() {
    const [year, setYear] = useState("");
    const [month, setMonth] = useState("");
    const [day, setDay] = useState("");
    const [time, setTime] = useState("");
    const [nextSeminar, setNextSeminar] = useState("12月02日");
    const [articles, setArticles] = useState([]);
    const [weatherData, setWeatherData] = useState({
        todayWeather: "",
        tomorrowWeather: "",
        maxTemp: "",
        minTemp: "",
        averageRainChance: "",
    });
    const [busSchedule, setBusSchedule] = useState([]);
    const [nextBus, setNextBus] = useState(null);
    const [upcomingBuses, setUpcomingBuses] = useState([]);
    const [schedules, setSchedules] = useState([]);
    const [futureSchedules, setFutureSchedules] = useState([]);

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
        const fetchRSS = async () => {
            try {
                const response = await fetch('http://202.13.169.105:5000/api/rss'); // バックエンドのAPIを呼び出す
                if (!response.ok) {
                    throw new Error('Failed to fetch RSS data');
                }
                const data = await response.json();
                setArticles(data);
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
        const fetchBusSchedule = async () => {
            try {
                const response = await fetch("http://202.13.169.105:5000/api/bus-schedule");
                const data = await response.json();
                setBusSchedule(data);
            } catch (error) {
                console.error("Error fetching bus schedule:", error);
            }
        };
        const updateNextBuses = (schedule) => {
            const now = new Date();
            const currentTime = now.getHours() * 60 + now.getMinutes(); // 分単位に変換
        
            const upcoming = schedule.filter((bus) => {
                const [hours, minutes] = bus.time.split(":").map(Number);
                const busTimeInMinutes = hours * 60 + minutes;
                return busTimeInMinutes >= currentTime;
            });
        
            if (upcoming.length > 0) {
                const formatRemainTime = (busTimeInMinutes) => {
                    const remain = busTimeInMinutes - currentTime;
                    const hours = Math.floor(remain / 60).toString().padStart(2, "0");
                    const minutes = (remain % 60).toString().padStart(2, "0");
                    return `${hours}:${minutes}`;
                };
        
                // 次のバス
                const [nextBusHours, nextBusMinutes] = upcoming[0].time.split(":").map(Number);
                const nextBusTimeInMinutes = nextBusHours * 60 + nextBusMinutes;
                setNextBus({
                    ...upcoming[0],
                    remain: formatRemainTime(nextBusTimeInMinutes),
                });
        
                // 次の2つのバス
                setUpcomingBuses(
                    upcoming.slice(1, 3).map((bus) => {
                        const [hours, minutes] = bus.time.split(":").map(Number);
                        const busTimeInMinutes = hours * 60 + minutes;
                        return {
                            ...bus,
                            remain: formatRemainTime(busTimeInMinutes),
                        };
                    })
                );
            } else {
                setNextBus(null);
                setUpcomingBuses([]);
            }
        };
        const fetchSchedule = async () => {
            try {
                const response = await fetch("http://202.13.169.105:5000/api/schedule");
                const data = await response.json();

                // 現在の日付を取得
                const today = new Date();
                const currentYear = today.getFullYear();
                const todayMonth = today.getMonth() + 1; // 月は0始まりなので+1
                const todayDay = today.getDate();
                const formattedToday = parseInt(`${String(todayMonth).padStart(2, "0")}${String(todayDay).padStart(2, "0")}`);

                // 跨年に対応した未来の予定を取得
                const upcoming = data.filter((item) => {
                    const itemMonthDay = parseInt(item.date);
                    const itemYear = itemMonthDay < formattedToday ? currentYear + 1 : currentYear; // 年を跨ぐ場合

                    // 比較用に現在の年月と予定の年月を組み立て
                    const todayYMD = parseInt(`${currentYear}${String(todayMonth).padStart(2, "0")}${String(todayDay).padStart(2, "0")}`);
                    const itemYMD = parseInt(`${itemYear}${String(itemMonthDay).padStart(4, "0")}`);

                    return itemYMD >= todayYMD;
                });

                // 未来の予定を3件だけ取得
                setFutureSchedules(upcoming.slice(0, 3));
            } catch (error) {
                console.error("Error fetching schedule data:", error);
            }
        };
        const fetchSeminarSchedule = async () => {
            try {
                const response = await fetch("http://202.13.169.105:5000/api/seminar");
                const data = await response.json();

                // 現在の日付と時刻を取得
                const now = new Date();
                const currentMonthDay = parseInt(
                    `${String(now.getMonth() + 1).padStart(2, "0")}${String(now.getDate()).padStart(2, "0")}`
                );
                const currentTime = now.getHours() * 100 + now.getMinutes();

                // 最も近いゼミを取得
                const upcoming = data
                    .map((item) => {
                        const seminarMonthDay = parseInt(item.date.slice(0, 4));
                        const seminarTime = parseInt(item.date.slice(4, 6)) * 100;
                        const isToday = seminarMonthDay === currentMonthDay;

                        return {
                            fullDate: item.date,
                            displayDate: `${parseInt(item.date.slice(0, 2))}月${parseInt(item.date.slice(2, 4))}日${item.date.slice(4, 6)}時〜`,
                            isUpcoming: seminarMonthDay > currentMonthDay || (isToday && seminarTime >= currentTime),
                        };
                    })
                    .filter((item) => item.isUpcoming)
                    .sort((a, b) => a.fullDate - b.fullDate);

                if (upcoming.length > 0) {
                    setNextSeminar(upcoming[0].displayDate);
                } else {
                    setNextSeminar("予定なし");
                }
            } catch (error) {
                console.error("Error fetching seminar schedule:", error);
                setNextSeminar("取得エラー");
            }
        };


        // 初回実行
        updateDateTime();
        fetchRSS();
        fetchWeatherData();
        fetchBusSchedule();
        updateNextBuses(busSchedule);
        fetchSchedule();
        fetchSeminarSchedule();

        // 1秒ごとに日付と時刻を更新
        const dateTimerInterval = setInterval(updateDateTime, 1000);
        // 1分ごとにニュースを取得
        const rssInterval = setInterval(fetchRSS, 60000);
        // 1分ごとに次のバスを更新
        const busInterval = setInterval(() => {
            updateNextBuses(busSchedule);
        }, 60000);
        // 1分ごとに次回のゼミの予定を取得
        const seminarInterval = setInterval(fetchSeminarSchedule(), 6000);

        // クリーンアップ
        return () => {
            clearInterval(dateTimerInterval);
            clearInterval(rssInterval);
            clearInterval(busInterval);
//            clearInterval(seminarInterval);
        };
    }, [busSchedule]);

    // 日付を整形する関数
    const formatDate = (yymm) => {
        const month = yymm.slice(0, 2);
        const day = yymm.slice(2, 4);
        return `${parseInt(month)}月${parseInt(day)}日`;
    };

    return (
        <div className="container">
            <div className="date-time-container">
                <div className="date-section">
                    <div className="month-section">{month}{day}</div>
                </div>
                <div className="time-section">{time}</div>
                <div className="seminar-section">
                    {nextSeminar}
                </div>
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
                        <img src="/icons/sun.svg" alt="晴れ"/>
                    </div>
                    <div className="max">{weatherData.maxTemp}℃</div>
                    <div className="min">{weatherData.minTemp}℃</div>
                    <div className="rain-chance">{weatherData.averageRainChance}</div>
                </div>
            </div>
                <div className="bus-containar">
                    <div className="bus-next">
                        <div className="bus-ntime">
                            {nextBus ? nextBus.time : "なし"}
                        </div>
                        <div className="bus-nremain">
                            {nextBus ? nextBus.remain : ""}
                        </div>
                    </div>
                    {upcomingBuses.map((bus, index) => (
                        <div className="bus-next" key={index}>
                            <div className="bus-time">{bus.time}</div>
                            <div className="bus-remain">{bus.remain}</div>
                        </div>
                    ))}
                </div>
            <div className="schedule-containar">
                {futureSchedules.map((schedule, index) => (
                    <div className="schedule-section" key={index}>
                        <div className="schedule-date">{formatDate(schedule.date)}  {schedule.content}</div>
                    </div>
                ))}
            </div>
            <div className="tkg-containar">
                tkg
            </div>
            <div className="znd-containar">
                <div className="znd-section">
                    <Canvas 
                        style={{ width: "100%", height: "100%" }}
                        camera={{ position: [0, 2, 5], fov:50 }}
                    >
                        {/* 環境光 */}
                        <ambientLight intensity={0.5} color="#ffffff" />
                        {/* 方向光 */}
                        <directionalLight position={[5, 10, 5]} intensity={1} />
                        {/* スポットライト */}
                        <spotLight position={[15, 20, 10]} angle={0.3} intensity={1.5} castShadow />
                        <ZndModel />
                        <OrbitControls enableZoom={true} />
                    </Canvas>
                </div>
                <div className="news-section">
                    {articles.map((article, index) => (
                        <div  className="news" key={index} style={{ borderBottom: '1px solid #ccc', paddingBottom: '10px' }}>
                            <strong className="news-title">{article.title}</strong>
                            <p className="news-description">{article.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default App;
