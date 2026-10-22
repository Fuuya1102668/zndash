from datetime import datetime

from nicegui import ui

from .config import NEWS_REFRESH_SECONDS, RAINFALL_REFRESH_SECONDS, WEATHER_REFRESH_SECONDS
from .services import fetch_news, fetch_rainfall_data, fetch_weather_forecast, format_temperature


def _weather_card():
    with ui.card().classes("w-full h-full p-4 bg-blue-50 flex flex-col gap-4"):
        ui.label("天気予報（石川県）").classes("text-lg font-bold text-blue-900")
        with ui.row().classes("w-full justify-around items-start"):
            with ui.column().classes("items-center gap-1"):
                ui.label("今日").classes("text-sm font-bold text-gray-500")
                today_telop = ui.label("--").classes("text-xl font-bold text-gray-800")
                today_temp = ui.label("最高 --℃ · 最低 --℃").classes("text-sm text-gray-600")
                today_rain = ui.label("☔ --%").classes("text-sm font-bold text-blue-600")
            ui.separator().props("vertical").classes("h-20")
            with ui.column().classes("items-center gap-1"):
                ui.label("明日").classes("text-sm font-bold text-gray-500")
                tomorrow_telop = ui.label("--").classes("text-xl font-bold text-gray-800")
                tomorrow_temp = ui.label("-- / -- ℃").classes("text-sm text-gray-600")
                tomorrow_rain = ui.label("☔ --%").classes("text-sm font-bold text-blue-600")
        ui.separator().classes("bg-blue-200")
        with ui.scroll_area().classes("h-24 w-full border rounded p-2 bg-white"):
            description = ui.label("読み込み中...").classes(
                "text-xs text-gray-600 whitespace-pre-wrap leading-relaxed"
            )

    async def update():
        data = await fetch_weather_forecast()
        if not data:
            description.set_text("天気予報を取得できませんでした")
            return

        today = data["today"]
        tomorrow = data["tomorrow"]
        today_telop.set_text(today["telop"])
        today_temp.set_text(
            f"最高 {format_temperature(today['max'])} · 最低 {format_temperature(today['min'])}"
        )
        today_rain.set_text(f"☔ {today['rain']}%")
        tomorrow_telop.set_text(tomorrow["telop"])
        tomorrow_temp.set_text(
            f"最高 {format_temperature(tomorrow['max'])} · 最低 {format_temperature(tomorrow['min'])}"
        )
        tomorrow_rain.set_text(f"☔ {tomorrow['rain']}%")
        description.set_text(data["description"])

    ui.timer(0.1, update, once=True)
    ui.timer(WEATHER_REFRESH_SECONDS, update)


def _rainfall_card():
    with ui.card().classes("w-full h-full p-4"):
        ui.label("直近の降水量").classes("text-lg font-bold text-gray-800")
        chart = ui.echart({
            "tooltip": {"trigger": "axis"},
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": {"type": "category", "data": [], "axisTick": {"alignWithLabel": True}},
            "yAxis": {"type": "value", "name": "mm/h", "minInterval": 0.1, "max": 5},
            "series": [{
                "name": "降水量", "type": "bar", "data": [],
                "itemStyle": {"color": "#5898d4"}, "barWidth": "60%",
            }],
        }).classes("w-full h-48")

    async def update():
        labels, values = await fetch_rainfall_data()
        if labels:
            chart.options["xAxis"]["data"] = labels
            chart.options["series"][0]["data"] = values
            chart.update()

    ui.timer(0.1, update, once=True)
    ui.timer(RAINFALL_REFRESH_SECONDS, update)


def _news_card(source_key, display_name, icon, header_classes, text_classes):
    with ui.card().classes("h-full flex flex-col shadow-sm"):
        with ui.row().classes(f"w-full p-2 {header_classes} items-center gap-2 rounded-t"):
            ui.icon(icon, size="xs").classes(text_classes)
            ui.label(display_name).classes(f"text-md font-bold {text_classes}")
        content = ui.column().classes("p-2 gap-3 w-full flex-grow")

    async def update():
        articles = await fetch_news(source_key)
        content.clear()
        with content:
            if not articles:
                ui.label("記事を取得できませんでした").classes("text-xs text-gray-500")
            for article in articles:
                with ui.column().classes("w-full gap-0"):
                    if article["link"]:
                        ui.link(article["title"], article["link"], new_tab=True).classes(
                            "text-sm font-bold leading-tight hover:text-blue-600 text-gray-800"
                        )
                    else:
                        ui.label(article["title"]).classes("text-sm font-bold text-gray-800")
                    ui.label(article["description"]).classes(
                        "text-xs text-gray-500 overflow-hidden line-clamp-1"
                    ).style("word-break: break-all;")
                ui.separator().classes("my-1")

    ui.timer(0.1, update, once=True)
    ui.timer(NEWS_REFRESH_SECONDS, update)


@ui.page("/")
def main_page():
    ui.colors(primary="#5898d4", secondary="#26a69a")
    ui.add_css("""
        .dashboard-grid { grid-template-columns: minmax(0, 1fr) !important; }
        @media (orientation: landscape) and (min-width: 1024px) {
            .dashboard-grid--weather { grid-template-columns: minmax(0, 2fr) minmax(0, 3fr) !important; }
            .dashboard-grid--three { grid-template-columns: repeat(3, minmax(0, 1fr)) !important; }
        }
    """)
    with ui.column().classes("w-full max-w-7xl mx-auto p-4 gap-4 bg-gray-50 min-h-screen"):
        with ui.row().classes("w-full justify-between items-center border-b pb-2"):
            ui.label("zndash ダッシュボード").classes("text-2xl font-bold text-gray-700")
            clock = ui.label().classes("text-3xl font-mono font-bold text-primary")
            ui.timer(1, lambda: clock.set_text(datetime.now().strftime("%H:%M:%S")))

        with ui.grid().classes("dashboard-grid dashboard-grid--weather w-full gap-4 grid-cols-1 md:grid-cols-3"):
            with ui.column():
                _weather_card()
            _rainfall_card()

        with ui.grid().classes("dashboard-grid dashboard-grid--three w-full gap-4 grid-cols-1 md:grid-cols-3"):
            _news_card("ITmedia", "ITmedia", "newspaper", "bg-red-100", "text-red-900")
            _news_card("Zenn", "Zenn（LLM）", "code", "bg-blue-100", "text-blue-900")
            _news_card("note", "note（Hugging Face）", "edit", "bg-green-100", "text-green-900")

