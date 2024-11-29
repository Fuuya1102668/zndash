// App.js
import React from "react";
import "./App.css";

function App() {
  return (
    <div className="container">
      <div className="section time">時刻</div>
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

