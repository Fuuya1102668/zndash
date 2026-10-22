"""An independent, portrait-first view of the dashboard's existing data."""

from datetime import datetime

from nicegui import ui

from .config import (
    RAINFALL_APP_ID,
    RAINFALL_REFRESH_SECONDS,
    WEATHER_REFRESH_SECONDS,
)
from .news_storage import get_latest_topics, get_pipeline_state
from .services import fetch_rainfall_data, fetch_weather_forecast, format_temperature


def _rainfall_options(labels, values):
    return {
        "animation": False,
        "grid": {"left": 38, "right": 10, "top": 14, "bottom": 28},
        "tooltip": {"trigger": "axis"},
        "xAxis": {
            "type": "category",
            "data": labels,
            "axisLabel": {"color": "#748092", "fontSize": 10, "interval": "auto"},
            "axisLine": {"lineStyle": {"color": "#dbe0e7"}},
        },
        "yAxis": {
            "type": "value",
            "name": "mm/h",
            "nameTextStyle": {"color": "#748092", "fontSize": 10},
            "axisLabel": {"color": "#748092", "fontSize": 10},
            "splitLine": {"lineStyle": {"color": "#e8ebf0"}},
            "minInterval": 0.1,
            "max": 5,
        },
        "series": [{
            "type": "bar",
            "data": values,
            "barMaxWidth": 18,
            "itemStyle": {"color": "#4b9cc2", "borderRadius": [4, 4, 0, 0]},
        }],
    }


@ui.page("/information-landscape")
def information_landscape_page():
    ui.add_head_html("""<style>
        body { background: #f2eee5; color: #17263b; }
        .landscape-shell { max-width: 820px; }
        .landscape-card { border: 1px solid #d9d4c9; box-shadow: 0 8px 24px #1830440b; }
        .weather-sky { background: #dce8e7; }
        .story-lead { background: #fffdf7; color: #17263b; border: 1px solid #d9d4c9; border-top: 5px solid var(--topic-accent); }
        .story-card { background: #fffdf7; border: 1px solid #e0d9cc; border-left: 4px solid var(--topic-accent); }
        .story-card .report-track { background: #e3ddd1; }
        .story-lead .report-track { background: #e3ddd1; }
        .story-number { color: var(--topic-accent); }
        .story-tag { color: var(--topic-accent); }
        .report-track { background: #ffffff30; border-radius: 99px; height: 5px; overflow: hidden; }
        .report-fill { background: var(--topic-accent); height: 100%; border-radius: inherit; }
        .keyword-chip { background: #17263b0c; }
    </style>""")

    with ui.column().classes("landscape-shell w-full mx-auto min-h-screen px-3 py-3 gap-3"):
        with ui.row().classes("w-full items-end justify-between border-b-2 border-slate-800 pb-2"):
            with ui.column().classes("gap-0"):
                ui.label("ISHIKAWA · DAILY SIGNAL").classes("text-[10px] font-bold tracking-[.24em] text-slate-500")
                ui.label("今日のネット、ざっくり。").classes("text-xl sm:text-2xl font-black tracking-tight")
            clock = ui.label().classes("text-lg font-mono text-gray-600")
            ui.timer(1, lambda: clock.set_text(datetime.now().strftime("%H:%M")))

        with ui.card().classes("landscape-card weather-sky w-full p-3 sm:p-4 rounded-2xl"):
            with ui.row().classes("w-full justify-between items-center"):
                with ui.column().classes("gap-1"):
                    ui.label("ISHIKAWA · WEATHER").classes("text-[9px] font-bold tracking-[.18em] text-gray-500")
                    today_text = ui.label("天気を読み込み中").classes("text-xl font-bold text-slate-800")
                with ui.column().classes("items-end gap-1"):
                    today_temp = ui.label("最高 --℃ · 最低 --℃").classes("text-sm font-bold text-slate-700")
                    today_rain = ui.label("降水確率 --%").classes("text-xs text-slate-600")
            with ui.row().classes("w-full items-center gap-2 mt-1"):
                ui.icon("water_drop").classes("text-sky-700 text-sm")
                rain_status = ui.label("雨量を取得中").classes("text-[10px] text-slate-500 shrink-0")
                rainfall_chart = ui.echart(_rainfall_options([], [])).classes("grow h-48 min-w-0")

        topics = ui.column().classes("w-full gap-2")
        updated_at = ui.label("").classes("w-full text-right text-xs text-gray-400")

    async def refresh_weather():
        weather_data = await fetch_weather_forecast()
        if weather_data:
            today = weather_data["today"]
            tomorrow = weather_data["tomorrow"]
            today_text.set_text(today["telop"])
            today_temp.set_text(
                f"最高 {format_temperature(today['max'])} · 最低 {format_temperature(today['min'])}"
            )
            today_rain.set_text(f"降水確率 {today['rain']}% · 明日 {tomorrow['telop']}")

    async def refresh_rainfall():
        labels, values = await fetch_rainfall_data()
        if labels:
            rainfall_chart.options.update(_rainfall_options(labels, values))
            rainfall_chart.update()
            rain_status.set_text(f"{labels[-1]} 更新 · mm")
        elif not RAINFALL_APP_ID:
            rain_status.set_text("雨量表示には YAHOO_WEATHER_APP_ID が必要")
        else:
            rain_status.set_text("雨量データを取得できません")

    async def refresh_news():
        groups = get_latest_topics()
        state = get_pipeline_state()
        topics.clear()
        total_articles = sum(group["count"] for group in groups)
        maximum_count = max((group["count"] for group in groups), default=1)
        palette = ["#f2784b", "#d6a82f", "#54a39a", "#7184d4", "#a76caa"]
        with topics:
            if not groups:
                ui.label("初回のニュース分析が終わると、話題がここに表示されます。")\
                    .classes("text-sm text-gray-500")
            def render_topic(group, index, lead=False, compact=False):
                accent = palette[index % len(palette)]
                card_classes = "story-lead" if lead else "story-card"
                padding = "p-2 sm:p-3" if compact else "p-3 sm:p-4"
                with ui.card().classes(f"{card_classes} w-full rounded-2xl {padding}")\
                    .style(f"--topic-accent: {accent}"):
                    with ui.row().classes("w-full items-start justify-between gap-2"):
                        with ui.column().classes("min-w-0 grow gap-0.5"):
                            eyebrow = "BIG STORY" if lead else f"TOPIC {index + 1:02d}"
                            ui.label(eyebrow).classes(
                                "story-tag text-[8px] font-black tracking-[.16em]"
                            )
                            ui.label(group["title"]).classes(
                                f"{'text-xl sm:text-2xl' if lead else ('text-sm sm:text-base' if compact else 'text-lg sm:text-xl')} font-black leading-tight tracking-tight text-slate-900"
                            )
                        with ui.column().classes("items-center shrink-0 gap-0"):
                            ui.label(str(group["count"])).classes(
                                f"story-number {'text-3xl sm:text-4xl' if lead else ('text-2xl sm:text-3xl' if compact else 'text-3xl')} font-black leading-none"
                            )
                            ui.label("記事").classes("text-[9px] font-bold tracking-widest text-slate-500")
                    ratio = min(1.0, group["count"] / maximum_count)
                    ui.label("最多話題との比").classes(
                        "mt-1 text-[7px] text-slate-500"
                    )
                    with ui.element("div").classes("report-track w-full mt-0.5").props(
                        f'title="{group["count"]}件 ÷ 最大{maximum_count}件"'
                    ):
                        ui.element("div").classes("report-fill").style(
                            f"--topic-accent:{accent}; width:{max(8, ratio * 100):.0f}%"
                        )
                    summary_color = "text-slate-700"
                    summary_size = "text-sm sm:text-base" if lead else ("text-[11px] sm:text-xs" if compact else "text-xs sm:text-sm")
                    ui.label(group["summary"]).classes(
                        f"mt-2 {summary_size} leading-snug font-semibold {summary_color}"
                    )
                    keywords = group.get("keywords", [])[:3]
                    if keywords:
                        with ui.row().classes("gap-1 mt-2"):
                            for keyword in keywords:
                                ui.label(keyword).classes(
                                    "keyword-chip rounded-full px-2 py-1 text-[9px] font-bold text-slate-600"
                                )
                    with ui.expansion("記事の見出しを見る", icon="notes")\
                        .classes("w-full mt-0.5 text-[11px] text-slate-600"):
                        for article in group["articles"]:
                            with ui.column().classes("w-full gap-1 border-l border-slate-300/50 pl-3 py-2"):
                                with ui.row().classes("w-full items-start justify-between gap-2"):
                                    ui.label(article["title"]).classes("text-[11px] font-semibold leading-snug")
                                    try:
                                        published = datetime.fromisoformat(article["published_at"]).astimezone()
                                        ui.label(published.strftime("%m/%d %H:%M"))\
                                            .classes("shrink-0 text-[9px] text-gray-400")
                                    except (TypeError, ValueError):
                                        pass
            visible_count = min(5, len(groups))
            if groups:
                render_topic(groups[0], 0, lead=True)
            if visible_count > 1:
                with ui.grid(columns=2).classes("w-full gap-2"):
                    for index, group in enumerate(groups[1:visible_count], start=1):
                        render_topic(group, index, compact=True)
            if len(groups) > visible_count:
                with ui.expansion(f"ほかの話題 {len(groups) - visible_count}件", icon="more_horiz")\
                    .classes("w-full rounded-xl bg-white/70 px-3 py-1 text-sm font-semibold"):
                    with ui.grid(columns=2).classes("w-full gap-2"):
                        for index, group in enumerate(groups[visible_count:], start=visible_count):
                            render_topic(group, index, compact=True)
        finished_at = state.get("last_finished_at")
        if finished_at:
            try:
                local_time = datetime.fromisoformat(finished_at).astimezone().strftime("%m/%d %H:%M")
            except ValueError:
                local_time = "時刻不明"
        else:
            local_time = "未実行"
        updated_at.set_text(
            f"直近24時間 {total_articles}記事 · 最終更新 {local_time} · 数字は登録フィード上の報道量"
        )

    ui.timer(0.2, refresh_weather, once=True)
    ui.timer(0.2, refresh_rainfall, once=True)
    ui.timer(0.2, refresh_news, once=True)
    ui.timer(WEATHER_REFRESH_SECONDS, refresh_weather)
    ui.timer(RAINFALL_REFRESH_SECONDS, refresh_rainfall)
    ui.timer(60, refresh_news)
