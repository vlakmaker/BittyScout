# FILE: ~/BittyScout/api.py

from fastapi import FastAPI, Query
from typing import Optional

# --- KEY CHANGE: Import the Celery tasks, not the logic functions ---
from tasks import (
    scrape_task,
    filter_task,
    notify_task,
    run_full_pipeline_task
)

app = FastAPI(
    title="BittyScout API",
    description="An API to trigger background jobs for scraping, filtering, and notifying.",
    version="1.0.0"
)

@app.get("/", summary="Health Check")
def read_root():
    """A simple health check endpoint to confirm the API is running."""
    return {"status": "BittyScout API is online and ready to accept tasks."}

@app.post("/scrape", status_code=202, summary="Queue a Scraping Task")
async def api_scrape(source: Optional[str] = Query(None, description="Optional: Specify a single source to scrape (e.g., 'Greenhouse').")):
    """
    Accepts a scrape request and queues it for background processing.
    Responds immediately.
    """
    print(f"API: Sending scrape task for source '{source or 'all'}' to the queue.")
    
    # Use .delay() to send the task to the Celery worker queue
    scrape_task.delay(source=source)
    
    return {"status": "accepted", "detail": "Scraping task has been successfully queued."}

@app.post("/filter", status_code=202, summary="Queue a Filtering Task")
async def api_filter():
    """

    Accepts a filter request and queues it for background processing.
    """
    print("API: Sending filter task to the queue.")
    filter_task.delay()
    return {"status": "accepted", "detail": "Filtering task has been successfully queued."}

@app.post("/notify", status_code=202, summary="Queue a Notification Task")
async def api_notify(channel: str = Query("console", description="The channel to notify ('console' or 'email').")):
    """
    Accepts a notify request and queues it for background processing.
    """
    print(f"API: Sending notify task for channel '{channel}' to the queue.")
    notify_task.delay(channel=channel)
    return {"status": "accepted", "detail": f"Notification task for channel '{channel}' has been successfully queued."}

@app.post("/run", status_code=202, summary="Queue the Full Pipeline Task")
async def api_run_full_pipeline():
    """
    Accepts a request to run the full pipeline and queues it for background processing.
    """
    print("API: Sending full pipeline task to the queue.")
    run_full_pipeline_task.delay()
    return {"status": "accepted", "detail": "Full scrape-filter-notify pipeline task has been successfully queued."}