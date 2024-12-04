import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
    const [year, setYear] = useState("");
    const [month, setMonth] = useState("");
    const [day, setDay] = useState("");
    const [time, setTime] = useState("");
    const [nextSeminar, setNextSeminar] = useState("12月02日");

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
                <div className="date-section">
                    <div className="month-section">{month}{day}</div>
                </div>
                <div className="time-section">{time}</div>
                <div className="seminar-section">
                    <div className="seminar-title">ゼミ</div>
                    <div className="seminar-date">12月02日10時～</div>
                </div>
            </div>
            <div className="weather-container">
                <div className="today-container">
                    <div className="icon-section">
                        <img src="/icons/sun.svg" alt="晴れ"/>
                    </div>
                    <div className="info-section">
                        <div className="info-title">降水量</div>
                        <div className="info-info">4mm</div>
                    </div>
                </div>
                <div className="tomorrow-container">
                    <div className="icon-section">
                        <img src="/icons/sun.svg" alt="晴れ"/>
                    </div>
                    <div className="info-section">
                        <div className="info-title">降水量</div>
                        <div className="info-info">133mm</div>
                    </div>
                </div>
            </div>
            <div className="slack-containar">Slack</div>
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
                    <div className="bus-next">
                        <div className="bus-time">19:50</div>
                        <div className="bus-remain">02:40</div>
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
                <img src="/icons/znd.png" alt="ずんだもん"/>
            </div>
        </div>
    );
}

export default App;
