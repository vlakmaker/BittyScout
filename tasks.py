# FILE: ~/BittyScout/tasks.py

import os
from celery import Celery

# Import the functions from your logic file
from logic import (
    run_scraping,
    run_filtering,
    run_notification,
    run_full_pipeline
)

# Get the Redis URL from an environment variable for flexibility,
# but default to the service name from docker-compose.
# This allows it to work both in Docker and potentially locally.
REDIS_URL = os.getenv("REDIS_URL", "redis://bittyscout-redis:6379/0")

# Initialize the Celery application
# The first argument is the name of the current module.
# The 'broker' and 'backend' tell Celery where to send/receive messages.
celery_app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

# --- Define the Background Tasks ---

@celery_app.task(name="tasks.scrape_task")
def scrape_task(source=None):
    """
    A Celery task that executes the run_scraping function from logic.py.
    The worker process will run this function when a message is received.
    """
    print(f"--- WORKER: Received scrape task for source: {source or 'all'} ---")
    try:
        run_scraping(source=source)
        print(f"--- WORKER: Scrape task finished successfully. ---")
        return {"status": "success"}
    except Exception as e:
        print(f"--- WORKER ERROR in scrape_task: {e} ---")
        return {"status": "error", "error_message": str(e)}

@celery_app.task(name="tasks.filter_task")
def filter_task():
    """A Celery task that executes the run_filtering function."""
    print(f"--- WORKER: Received filter task. ---")
    try:
        run_filtering()
        print(f"--- WORKER: Filter task finished successfully. ---")
        return {"status": "success"}
    except Exception as e:
        print(f"--- WORKER ERROR in filter_task: {e} ---")
        return {"status": "error", "error_message": str(e)}


@celery_app.task(name="tasks.notify_task")
def notify_task(channel="console"):
    """A Celery task that executes the run_notification function."""
    print(f"--- WORKER: Received notify task for channel: {channel} ---")
    try:
        run_notification(channel=channel)
        print(f"--- WORKER: Notify task for channel '{channel}' finished successfully. ---")
        return {"status": "success"}
    except Exception as e:
        print(f"--- WORKER ERROR in notify_task: {e} ---")
        return {"status": "error", "error_message": str(e)}


@celery_app.task(name="tasks.run_full_pipeline_task")
def run_full_pipeline_task():
    """A Celery task that executes the full pipeline."""
    print(f"--- WORKER: Received full pipeline task. ---")
    try:
        run_full_pipeline()
        print(f"--- WORKER: Full pipeline task finished successfully. ---")
        return {"status": "success"}
    except Exception as e:
        print(f"--- WORKER ERROR in run_full_pipeline_task: {e} ---")
        return {"status": "error", "error_message": str(e)}