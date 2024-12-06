const express = require('express');
const Parser = require('rss-parser');
const cors = require('cors');

const app = express();
const parser = new Parser();

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

// サーバーを起動
const PORT = 5000; // バックエンドはポート5000で実行
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
