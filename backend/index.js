const Parser = require('rss-parser');
const parser = new Parser();

(async () => {
    const feed = await parser.parseURL('https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml');
    console.log('Top 3 Articles:');
    feed.items.slice(0,3).forEach((item,index) => {
        console.log(`\n${index + 1}. Title: ${item.title}`);
        console.log(`Description: ${item.contentSnippet || item.content || 'No description available'}`);
    });
})();

