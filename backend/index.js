const express = require('express');
const Parser = require('rss-parser');
const axios = require("axios");
const cors = require('cors');
const fs = require("fs");
const path = require("path");
const { parseStringPromise } = require("xml2js");

const app = express();
const parser = new Parser();
const PORT = 5000;

// CORSを有効化
app.use(cors());

// ITmedisのニュースのエンドポイント
app.get('/api/rss', async (req, res) => {
  try {
    const feed = await parser.parseURL('https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml');
    const topArticles = feed.items.slice(0, 3).map(item => ({
      title: item.title,
      description: item.contentSnippet || item.content || 'No description available',
    }));
    res.json(topArticles);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Failed to fetch RSS feed' });
  }
});

app.get("/api/rainfall", async (req, res) => {
    try {
        console.log("お天気データ取得するよ")
        const response = await axios.get("https://map.yahooapis.jp/weather/V1/place", {
            params: {
                coordinates: "136.571755,36.484950",
                appid: "dj00aiZpPWpRQlpaY29rMUNLQyZzPWNvbnN1bWVyc2VjcmV0Jng9NDY-",
                interval: 5,
                past: 0,
            },
        });
        console.log("お天気データ取得したよ")

        // XMLをJSONに変換
        const jsonResult = await parseStringPromise(response.data);

        const weatherList =
            jsonResult.YDF.Feature[0].Property[0].WeatherList[0].Weather.map((weather) => ({
                time: weather.Date[0],
                rainfall: parseFloat(weather.Rainfall[0]),
            }));

        res.json(weatherList);
    } catch (error) {
        console.error("Error fetching rainfall data:", error.message || error);
        res.status(500).json({ error: "Failed to fetch rainfall data" });
    }
});

app.get("/api/weather", async (req, res) => {
    try {
        const response = await axios.get("https://weather.tsukumijima.net/api/forecast/city/170010");
        const data = response.data;

        // 必要なデータを抽出
        const todayWeather = data.description.bodyText; // 今日の天気説明文
        const tomorrowWeather = data.forecasts[1].telop; // 明日の天気
        const maxTemp = data.forecasts[1].temperature.max?.celsius || "N/A"; // 明日の最高気温
        const minTemp = data.forecasts[1].temperature.min?.celsius || "N/A"; // 明日の最低気温

        // 明日の降水確率（平均値を計算）
        const rainChances = [
            data.forecasts[1].chanceOfRain.T06_12,
            data.forecasts[1].chanceOfRain.T12_18,
            data.forecasts[1].chanceOfRain.T18_24,
        ];
        const rainChanceValues = rainChances
            .map((chance) => parseInt(chance.replace("%", "")) || 0); // %を取り除いて数値化
        const averageRainChance = (rainChanceValues.reduce((sum, value) => sum + value, 0) / rainChanceValues.length) || 0;

        // レスポンス
        res.json({
            todayWeather,
            tomorrowWeather,
            maxTemp,
            minTemp,
            averageRainChance: `${Math.round(averageRainChance)}%`,
        });
    } catch (error) {
        console.error("Error fetching weather data:", error);
        res.status(500).json({ error: "Failed to fetch weather data" });
    }
});

//バスの時刻表を取得するエンドポイント
app.get("/api/bus-schedule", (req, res) => {
    const filePath = path.join(__dirname, "bus-schedule.json");

    fs.readFile(filePath, "utf-8", (err, data) => {
        if (err) {
            console.error("Error reading bus-schedule.json:", err);
            res.status(500).json({ error: "Failed to load bus schedule" });
        } else {
            const now = new Date();
            const currentTime = now.getHours() * 60 + now.getMinutes(); // 現在時刻を分に変換

            const schedule = JSON.parse(data).map((bus) => {
                const [hours, minutes] = bus.time.split(":").map(Number);
                const busTimeInMinutes = hours * 60 + minutes;

                // 残り時間を計算
                const remainMinutes = busTimeInMinutes - currentTime;
                bus.remain =
                    remainMinutes > 0
                        ? `${Math.floor(remainMinutes / 60)}:${remainMinutes % 60}`
                        : "";
                return bus;
            });

            res.json(schedule);
        }
    });
});

// スケジュールを取得するエンドポイント
app.get("/api/schedule", (req, res) => {
    try {
        const data = fs.readFileSync("./schedule.json", "utf-8");
        const schedule = JSON.parse(data);
        res.json(schedule);
    } catch (error) {
        console.error("Error reading schedule.json:", error);
        res.status(500).json({ error: "Failed to fetch schedule" });
    }
});

// ゼミの日程を取得
app.get("/api/seminar", (req, res) => {
    try {
        const data = fs.readFileSync("./seminar.json", "utf-8");
        const schedule = JSON.parse(data);
        res.json(schedule);
    } catch (error) {
        console.error("Error reading schedule.json:", error);
        res.status(500).json({ error: "Failed to fetch schedule" });
    }
});

// サーバーを起動
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
