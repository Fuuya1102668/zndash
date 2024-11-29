// App.js
import React from "react";
import "./App.css";

function App() {
  return (
    <div className="container">
      <div className="section time">時刻</div>
      <div className="section weather">
        <div className="subsection">天気</div>
        <div className="subsection">降水量</div>
      </div>
      <div className="section">
        <div className="subsection">バス</div>
        <div className="subsection">Znd</div>
      </div>
      <div className="section slack">Slack</div>
    </div>
  );
}

export default App;
