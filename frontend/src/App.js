//import React, { useState, useEffect } from "react";
//import { Canvas } from "@react-three/fiber";
//import { OrbitControls, useGLTF } from "@react-three/drei";
//import "./App.css";

import React, { useState, useEffect, useRef, } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";
import { FBXLoader } from "three/examples/jsm/loaders/FBXLoader";
import "./App.css";

//function ZndModel() {
//     const { scene } = useGLTF("/models/znd-model.glb"); // 3Dモデルのパス
//     return <primitive object={scene} scale={2} />;
//}

function ZndModel() {
    const modelRef = useRef();
    const mixerRef = useRef();
  
    useEffect(() => {
        const loader = new FBXLoader();
        loader.load(
            "/models/znd-model.fbx", // FBXファイルのパス
            (object) => {
                object.scale.set(0.05, 0.05, 0.05); // サイズ調整
                object.position.set(0, -4, -4); // モデル全体を下に移動
                modelRef.current.add(object);
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
                const response = await fetch('http://localhost:5000/api/rss'); // バックエンドのAPIを呼び出す
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

        // 初回実行
        updateDateTime();
        fetchRSS();

        // 1秒ごとに日付と時刻を更新
        const timer = setInterval(updateDateTime, 1000);
        // 1分ごとに実行
        const interval = setInterval(fetchRSS, 60000);

        // クリーンアップ
        return () => clearInterval(timer);
    }, []);

    return (
        <div className="container">
            <div className="date-time-container">
                <div className="date-section">
                    <div className="month-section">{month}{day}</div>
                </div>
                <div className="time-section">{time}</div>
                <div className="seminar-section">
                    12月02日10時～
                </div>
            </div>
            <div className="weather-container">
                <div className="rain-section">
                    降水量
                </div>
                <div className="info-section">
                    晴れ　時々　雨
                </div>
                <div className="tomorrow-section">
                    <img src="/icons/sun.svg" alt="晴れ"/>
                </div>
            </div>
                <div className="bus-containar">
                    <div className="bus-next">
                        <div className="bus-ntime">17:10</div>
                        <div className="bus-nremain">00:00</div>
                    </div>
                    <div className="bus-next">
                        <div className="bus-time">17:40</div>
                        <div className="bus-remain">00:30</div>
                    </div>
                    <div className="bus-next">
                        <div className="bus-time">18:30</div>
                        <div className="bus-remain">01:20</div>
                    </div>
                </div>
            <div className="schedule-containar">
                <div className="schedule-section">
                    <div className="schedule-date">
                        01月08日
                    </div>
                    <div className="schedule-sentence">
                        月曜授業
                    </div>
                </div>
                <div className="schedule-section">
                    <div className="schedule-date">
                        01月22日
                    </div>
                    <div className="schedule-sentence">
                        PD3予稿・本文提出 
                    </div>
                </div>
                <div className="schedule-section">
                    <div className="schedule-date">
                        02月14日
                    </div>
                    <div className="schedule-sentence">
                        PD3公開審査会
                    </div>
                </div>
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
                            <p>{article.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default App;
