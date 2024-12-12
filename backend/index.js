const express = require('express');
const Parser = require('rss-parser');
const axios = require("axios");
const cors = require('cors');
const { parseStringPromise } = require("xml2js");

const app = express();
const parser = new Parser();
const PORT = 5000;

// CORSを有効化
app.use(cors());

// APIエンドポイントを作成
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
        const response = await axios.get("https://map.yahooapis.jp/weather/V1/place", {
            params: {
                coordinates: "136.571755,36.484950",
                appid: "dj00aiZpPWpRQlpaY29rMUNLQyZzPWNvbnN1bWVyc2VjcmV0Jng9NDY-",
                interval: 5,
                past: 2,
            },
        });
        console.log("データ取得\n")

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

// サーバーを起動
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
