import asyncio

from nicegui import app, ui

from . import dashboard  # noqa: F401  registers the dashboard page
from . import information_landscape  # noqa: F401  registers an independent page
from .news_pipeline import run_hourly_news_pipeline
from .news_storage import initialize_storage


_news_pipeline_task = None


async def _start_news_pipeline():
    global _news_pipeline_task
    initialize_storage()
    if _news_pipeline_task is None or _news_pipeline_task.done():
        _news_pipeline_task = asyncio.create_task(
            run_hourly_news_pipeline(), name="zndash-hourly-news-pipeline"
        )


async def _stop_news_pipeline():
    global _news_pipeline_task
    if _news_pipeline_task and not _news_pipeline_task.done():
        _news_pipeline_task.cancel()
        await asyncio.gather(_news_pipeline_task, return_exceptions=True)
    _news_pipeline_task = None


app.on_startup(_start_news_pipeline)
app.on_shutdown(_stop_news_pipeline)


def main():
    ui.run(title="zndash", language="ja", favicon="⛅", reload=False, show=False)
