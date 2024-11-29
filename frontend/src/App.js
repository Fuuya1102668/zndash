
import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [time, setTime] = useState("");

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const formattedTime = now.toLocaleTimeString("ja-JP", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
      setTime(formattedTime);
    };

    // 初回実行
    updateTime();

    // 1秒ごとに時刻を更新
    const timer = setInterval(updateTime, 1000);

    // クリーンアップ
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="container">
      {/* 時刻欄にリアルタイム時計を表示 */}
      <div className="section time">{time}</div>
      <div className="section weather">
        <div className="weather-icon">☀️</div>
        <div className="weather-info">降水量</div>
      </div>
      <div className="section content">
        <div className="subsection">バス</div>
        <div className="subsection">Znd</div>
      </div>
      <div className="section slack">Slack</div>
    </div>
  );
}

export default App;
