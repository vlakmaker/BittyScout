# utils/db_utils.py

import sqlite3
import os
from datetime import datetime, timezone

# --- Database Setup ---
DB_NAME = os.getenv("DB_NAME", "bittyscout.db")
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(PROJECT_ROOT, DB_NAME)

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_jobs_table_if_not_exist():
    """Creates the 'jobs' table with all required columns for all agents."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_url TEXT NOT NULL UNIQUE,
            platform_job_id TEXT,
            platform_source TEXT NOT NULL,
            company_name TEXT,
            title TEXT NOT NULL,
            location TEXT,
            department TEXT,
            date_posted_on_platform TEXT,
            date_fetched TEXT NOT NULL,
            last_seen_on_platform TEXT NOT NULL,
            api_provided_description TEXT,
            full_description_text TEXT,
            is_relevant BOOLEAN DEFAULT NULL,
            relevance_score REAL DEFAULT 0.0,
            tags TEXT,
            notified_on TEXT DEFAULT NULL
        );
        """
        cursor.execute(create_table_sql)
        conn.commit()
        conn.close()
        print(f"✅ BittyScout 'jobs' table ensured in '{DB_PATH}'")
    except sqlite3.Error as e:
        print(f"❌ ERROR creating jobs table: {e}")
        exit(1)

def add_or_update_job(job_data: dict) -> tuple[str, int | None]:
    """Inserts a new job or updates the last_seen_on_platform timestamp."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    job_url = job_data.get("job_url")
    try:
        cursor.execute("SELECT id FROM jobs WHERE job_url = ?", (job_url,))
        existing_job = cursor.fetchone()
        if existing_job:
            job_id = existing_job['id']
            cursor.execute("UPDATE jobs SET last_seen_on_platform = ? WHERE id = ?", (now_iso, job_id))
            conn.commit()
            return "updated", job_id
        else:
            insert_sql = """
            INSERT INTO jobs (
                job_url, platform_job_id, platform_source, company_name, title, 
                location, department, date_posted_on_platform, date_fetched, 
                last_seen_on_platform, api_provided_description, full_description_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            data_tuple = (
                job_url, job_data.get("platform_job_id"), job_data.get("platform_source"),
                job_data.get("company_name"), job_data.get("title"), job_data.get("location"),
                job_data.get("department"), job_data.get("date_posted_on_platform"),
                now_iso, now_iso, job_data.get("api_provided_description"),
                job_data.get("full_description_text")
            )
            cursor.execute(insert_sql, data_tuple)
            new_job_id = cursor.lastrowid
            conn.commit()
            return "inserted", new_job_id
    except sqlite3.Error as e:
        print(f"❌ Database error for job '{job_url}': {e}")
        return "error", None
    finally:
        conn.close()

def get_unprocessed_jobs() -> list[sqlite3.Row]:
    """Fetches jobs that have not been processed by the Filter Agent."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT id, title, api_provided_description, full_description_text FROM jobs WHERE is_relevant IS NULL"
    cursor.execute(query)
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def update_job_analysis(job_id: int, is_relevant: bool, relevance_score: float, tags: str):
    """Updates a job record with the results from the Filter Agent."""
    conn = get_db_connection()
    cursor = conn.cursor()
    update_sql = "UPDATE jobs SET is_relevant = ?, relevance_score = ?, tags = ? WHERE id = ?"
    try:
        cursor.execute(update_sql, (is_relevant, relevance_score, tags, job_id))
        conn.commit()
    finally:
        conn.close()

# --- Functions for the Notifier Agent ---

def get_new_relevant_jobs() -> list[sqlite3.Row]:
    """Fetches relevant jobs that have not been notified about yet."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT title, company_name, location, job_url, relevance_score, tags
    FROM jobs WHERE is_relevant = 1 AND notified_on IS NULL
    ORDER BY relevance_score DESC, date_fetched DESC
    """
    cursor.execute(query)
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def mark_jobs_as_notified(job_urls: list[str]):
    """Updates the notified_on timestamp for a list of job URLs."""
    if not job_urls: return
    now_iso = datetime.now(timezone.utc).isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ','.join('?' for _ in job_urls)
    update_sql = f"UPDATE jobs SET notified_on = ? WHERE job_url IN ({placeholders})"
    try:
        cursor.execute(update_sql, [now_iso] + job_urls)
        conn.commit()
    finally:
        conn.close()
