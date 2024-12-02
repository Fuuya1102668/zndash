import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [year, setYear] = useState("");
  const [month, setMonth] = useState("");
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [nextSeminar, setNextSeminar] = useState("12月02日");

  useEffect(() => {
    const updateDateTime = () => {
      const now = new Date();

      // 日付のフォーマット
      const formattedYear = `${now.getFullYear()}年`;
      const formattedMonth = `${String(now.getMonth() + 1).padStart(2, "0")}月`;
      const formattedDate = `${String(now.getDate()).padStart(2, "0")}日`;

      // 時刻のフォーマット
      const formattedTime = now.toLocaleTimeString("ja-JP", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });

      setYear(formattedYear);
      setMonth(formattedMonth);
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
      <div className="date-time-container">
        <div className="date-section">{year}<br>{month}{date}</div>
        <div className="time-section">{time}</div>
        <div className="seminar-section">
            <div className="seminar-title">ゼミ</div>
            <div className="seminar-date">12月02日10時～</div>
        </div>
      </div>
      <div className="weather-container">
        <div className="icon-section">
          <img src="/icons/sun.svg" alt="晴れ"/>
        </div>
        <div className="info-section">
          <div className="info-title">降水量</div>
          <div className="info-info">4mm</div>
        </div>
      </div>
      <div className="slack-containar">Slack</div>
      <div className="bus-containar">
        バス
      </div>
      <div className="schedule-containar">
        予定
      </div>
      <div className="znd-containar">
        <img src="/icons/sun.svg" alt="晴れ"/>
      </div>
    </div>
  );
}

export default App;
