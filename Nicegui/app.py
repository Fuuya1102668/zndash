from nicegui import ui, run
from datetime import datetime
import httpx
import xml.etree.ElementTree as ET
import feedparser
import asyncio

# ==========================================
# 1. 天気予報データ取得 (Tsukumijima API)
# ==========================================

async def fetch_weather_forecast():
    """
    天気予報APIからデータを取得し、今日と明日の詳細情報を返す
    """
    url = "https://weather.tsukumijima.net/api/forecast/city/170010" # 石川県
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            def parse_forecast(forecast_data):
                if not forecast_data:
                    return None
                
                telop = forecast_data['telop']
                t_max = forecast_data['temperature']['max']['celsius'] if forecast_data['temperature']['max'] else "--"
                t_min = forecast_data['temperature']['min']['celsius'] if forecast_data['temperature']['min'] else "--"

                rain_probs = []
                for key in ['T00_06', 'T06_12', 'T12_18', 'T18_24']:
                    val_str = forecast_data['chanceOfRain'].get(key, '--')
                    if val_str and val_str != '--':
                        try:
                            rain_probs.append(int(val_str.replace('%', '')))
                        except ValueError:
                            pass
                
                avg_rain = sum(rain_probs) // len(rain_probs) if rain_probs else 0
                
                return {
                    "telop": telop,
                    "max": t_max,
                    "min": t_min,
                    "rain": avg_rain
                }

            return {
                "description": data['description']['bodyText'],
                "today": parse_forecast(data['forecasts'][0]),  # 今日
                "tomorrow": parse_forecast(data['forecasts'][1]) # 明日
            }

    except Exception as e:
        print(f"Weather Forecast Error: {e}")
        return None

# ==========================================
# 2. 降水量グラフ取得 (Yahoo! API)
# ==========================================

async def fetch_rainfall_data():
    url = "https://map.yahooapis.jp/weather/V1/place"
    params = {
        "coordinates": "136.571755,36.484950",
        "appid": "dj00aiZpPWpRQlpaY29rMUNLQyZzPWNvbnN1bWVyc2VjcmV0Jng9NDY-",
        "interval": 5,
        "past": 0,
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=5.0)
            response.raise_for_status()
            ns = {'ns': 'http://olp.yahooapis.jp/ydf/1.0'}
            root = ET.fromstring(response.text)
            weather_elements = root.findall('.//ns:Weather', ns)
            labels = []
            values = []
            for weather in weather_elements:
                date_str = weather.find('ns:Date', ns).text
                rainfall = float(weather.find('ns:Rainfall', ns).text)
                time_label = f"{date_str[-4:-2]}:{date_str[-2:]}"
                labels.append(time_label)
                values.append(rainfall)
            return labels, values
    except Exception as e:
        print(f"Yahoo Rain API Error: {e}")
        return [], []

# ==========================================
# 3. ニュース取得 (feedparser)
# ==========================================

def _parse_feed_sync(url):
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:3]:
            description = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
            if not description and 'content' in entry:
                 description = entry.content.value
            articles.append({
                'title': entry.title,
                'link': entry.link,
                'description': description
            })
        return articles
    except:
        return []

async def fetch_news_source(source_key):
    urls = {
        'ITmedia': 'https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml',
        'Zenn': 'https://zenn.dev/topics/llm/feed',
        'note': 'https://note.com/hashtag/huggingface/rss'
    }
    target_url = urls.get(source_key)
    if not target_url: return []
    return await run.io_bound(_parse_feed_sync, target_url)

# ==========================================
# 4. UIコンポーネント
# ==========================================

def weather_forecast_card():
    """今日・明日の天気予報を表示するカード"""
    with ui.card().classes('w-full h-full p-4 bg-blue-50 flex flex-col gap-4'):
        ui.label('天気予報 (石川県)').classes('text-lg font-bold text-blue-900')

        with ui.row().classes('w-full justify-around items-start'):
            # 今日
            with ui.column().classes('items-center gap-1'):
                ui.label('今日').classes('text-sm font-bold text-gray-500')
                today_telop = ui.label('--').classes('text-xl font-bold text-gray-800')
                today_temp = ui.label('-- / -- ℃').classes('text-sm text-gray-600')
                today_rain = ui.label('☔ --%').classes('text-sm font-bold text-blue-600')

            ui.separator().props('vertical').classes('h-20')

            # 明日
            with ui.column().classes('items-center gap-1'):
                ui.label('明日').classes('text-sm font-bold text-gray-500')
                tomorrow_telop = ui.label('--').classes('text-xl font-bold text-gray-800')
                tomorrow_temp = ui.label('-- / -- ℃').classes('text-sm text-gray-600')
                tomorrow_rain = ui.label('☔ --%').classes('text-sm font-bold text-blue-600')

        ui.separator().classes('bg-blue-200')
        
        with ui.scroll_area().classes('h-24 w-full border rounded p-2 bg-white'):
            desc_label = ui.label('読み込み中...').classes('text-xs text-gray-600 whitespace-pre-wrap leading-relaxed')

    async def update():
        data = await fetch_weather_forecast()
        if data:
            today = data['today']
            today_telop.set_text(today['telop'])
            today_temp.set_text(f"{today['max']}℃ / {today['min']}℃")
            today_rain.set_text(f"☔ {today['rain']}%")

            tomorrow = data['tomorrow']
            tomorrow_telop.set_text(tomorrow['telop'])
            tomorrow_temp.set_text(f"{tomorrow['max']}℃ / {tomorrow['min']}℃")
            tomorrow_rain.set_text(f"☔ {tomorrow['rain']}%")

            desc_label.set_text(data['description'])

    ui.timer(0.1, update, once=True)
    ui.timer(3600, update)

def rainfall_chart_component():
    """降水量グラフ"""
    chart = ui.echart({
        'tooltip': {'trigger': 'axis'},
        'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': True},
        'xAxis': {'type': 'category', 'data': [], 'axisTick': {'alignWithLabel': True}},
        'yAxis': {
            'type': 'value', 
            'name': 'mm', 
            'minInterval': 0.1,
            'max': 10  # ★ここを10mmに固定
        },
        'series': [{'name': '降水量', 'type': 'bar', 'data': [], 'itemStyle': {'color': '#5898d4'}, 'barWidth': '60%'}]
    }).classes('w-full h-40')

    async def update():
        labels, values = await fetch_rainfall_data()
        if labels:
            chart.options['xAxis']['data'] = labels
            chart.options['series'][0]['data'] = values # リストの0番目を指定
            chart.update()

    ui.timer(0.1, update, once=True)
    ui.timer(300, update)

def news_card_component(source_key, display_name, icon, bg_color, text_color):
    """ニュースカード"""
    with ui.card().classes('h-full flex flex-col shadow-sm'):
        with ui.row().classes(f"w-full p-2 {bg_color} items-center gap-2 rounded-t"):
            ui.icon(icon, size='xs').classes(text_color)
            ui.label(display_name).classes(f"text-md font-bold {text_color}")
        
        content_area = ui.column().classes('p-2 gap-3 w-full flex-grow')

        async def update():
            articles = await fetch_news_source(source_key)
            content_area.clear()
            with content_area:
                for article in articles:
                    with ui.column().classes('w-full gap-0'):
                        ui.link(article['title'], article['link'], new_tab=True).classes(
                            'text-sm font-bold leading-tight hover:text-blue-600 text-gray-800'
                        )
                        ui.label(article['description']).classes(
                            'text-xs text-gray-500 overflow-hidden line-clamp-1'
                        ).style('word-break: break-all;')
                    ui.separator().classes('last:hidden my-1')

        ui.timer(0.1, update, once=True)
        ui.timer(1800, update)

# ==========================================
# 5. メインページレイアウト
# ==========================================

@ui.page('/')
def main_page():
    ui.colors(primary='#5898d4', secondary='#26a69a')
    
    with ui.column().classes('w-full max-w-7xl mx-auto p-4 gap-4 bg-gray-50 min-h-screen'):
        
        # ヘッダー
        with ui.row().classes('w-full justify-between items-center border-b pb-2'):
            ui.label('My Dashboard').classes('text-2xl font-bold text-gray-700')
            clock = ui.label().classes('text-3xl font-mono font-bold text-primary')
            ui.timer(1.0, lambda: clock.set_text(datetime.now().strftime('%H:%M:%S')))

        # 上段：天気情報
        with ui.grid().classes('w-full gap-4 grid-cols-1 md:grid-cols-3'):
            with ui.column().classes('col-span-1'):
                weather_forecast_card()
            
            with ui.card().classes('col-span-1 md:col-span-2 p-4'):
                with ui.row().classes('items-center gap-2 mb-2'):
                    ui.icon('umbrella', size='sm', color='primary')
                    ui.label('直近の降水量 (Yahoo! YOLP)').classes('text-lg font-bold text-gray-800')
                rainfall_chart_component()

        # 下段：ニュースエリア
        with ui.grid().classes('w-full gap-4 grid-cols-1 md:grid-cols-3'):
            news_card_component('ITmedia', 'ITmedia', 'newspaper', 'bg-red-100', 'text-red-900')
            news_card_component('Zenn', 'Zenn (LLM)', 'code', 'bg-blue-100', 'text-blue-900')
            news_card_component('note', 'note (HF)', 'edit', 'bg-green-100', 'text-green-900')

ui.run(title='Dashboard', language='ja', favicon='⛅')
