
import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");

  useEffect(() => {
    const updateDateTime = () => {
      const now = new Date();
      
      // 日付のフォーマット
      const formattedDate = `${now.getFullYear()}年${String(now.getMonth()+1).padStart(2, "0")}月${String(now.getDate()).padStart(2, "0")}日`;

      // 時刻のフォーマット
      const formattedTime = now.toLocaleTimeString("ja-JP", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });

      setDate(formattedDate);
      setTime(formattedTime);
    };

    // 初回実行
    updateDateTime();

    // 1秒ごとに日付と時刻を更新
    const timer = setInterval(updateDateTime, 1000);

    // クリーンアップ
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="container">
      <div className="section date-time">
          <div className="date">{date}</div>
          <div className="time">{time}</div>
      </div>

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

