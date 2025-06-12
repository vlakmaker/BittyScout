import sqlite3
import os
from datetime import datetime

# --- Database Configuration ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_NAME = os.getenv("BITTYSCOUT_DB_NAME", "bittyscout.db")
DB_PATH = os.path.join(PROJECT_ROOT, DB_NAME)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_jobs_table_if_not_exist():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_url TEXT UNIQUE NOT NULL,
                platform_job_id TEXT,
                platform_source TEXT NOT NULL,
                company_name TEXT,
                title TEXT NOT NULL,
                location TEXT,
                department TEXT,
                date_posted_on_platform TEXT,
                date_fetched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen_on_platform TIMESTAMP,
                api_provided_description TEXT,
                full_description_text TEXT,
                is_relevant_to_criteria BOOLEAN,
                ai_relevance_score REAL,
                ai_filter_model_used TEXT,
                llm_summary TEXT,
                summarizer_model_used TEXT,
                sent_in_digest_at TIMESTAMP,
                CONSTRAINT unique_job_on_platform UNIQUE (platform_source, platform_job_id)
            );
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_job_url ON jobs (job_url);')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_platform_id ON jobs (platform_source, platform_job_id);')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_needs_filtering ON jobs (is_relevant_to_criteria, date_fetched);')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_needs_summary ON jobs (is_relevant_to_criteria, llm_summary, date_fetched);')

        conn.commit()
        print(f"✅ BittyScout 'jobs' table ensured in '{DB_PATH}'")
    except Exception as e:
        print(f"❌ ERROR creating jobs table: {e}")
    finally:
        conn.close()


def add_or_update_job(job_data: dict) -> tuple[str, int | None]:
    conn = get_db_connection()
    cursor = conn.cursor()
    job_url = job_data.get("job_url")
    if not job_url:
        return "error_no_url", None

    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    try:
        cursor.execute("SELECT id FROM jobs WHERE job_url = ?", (job_url,))
        row = cursor.fetchone()

        if row:
            cursor.execute("UPDATE jobs SET last_seen_on_platform = ? WHERE id = ?", (now, row["id"]))
            conn.commit()
            return "updated_seen", row["id"]

        cursor.execute('''
            INSERT INTO jobs (
                job_url, platform_job_id, platform_source, company_name, title, location, department,
                date_posted_on_platform, api_provided_description, full_description_text,
                date_fetched, last_seen_on_platform
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_data["job_url"], job_data.get("platform_job_id"), job_data.get("platform_source", "Unknown"),
            job_data.get("company_name"), job_data.get("title", "No Title"), job_data.get("location"),
            job_data.get("department"), job_data.get("date_posted_on_platform"),
            job_data.get("api_provided_description"), job_data.get("full_description_text"),
            now, now
        ))
        conn.commit()
        return "inserted", cursor.lastrowid

    except sqlite3.IntegrityError:
        return "integrity_error", None
    except Exception as e:
        print(f"❌ ERROR add_or_update_job: {e}")
        return "error", None
    finally:
        conn.close()


def get_jobs_for_filtering(limit: int = 10) -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT id, job_url, title, full_description_text, api_provided_description
            FROM jobs WHERE is_relevant_to_criteria IS NULL
            ORDER BY date_fetched DESC LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"❌ ERROR get_jobs_for_filtering: {e}")
        return []
    finally:
        conn.close()


def update_job_relevance(job_url: str, is_relevant: bool, score: float, model_used: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE jobs SET is_relevant_to_criteria = ?, ai_relevance_score = ?, ai_filter_model_used = ?
            WHERE job_url = ?
        ''', (is_relevant, score, model_used, job_url))
        conn.commit()
    except Exception as e:
        print(f"❌ ERROR update_job_relevance: {e}")
    finally:
        conn.close()


def get_jobs_for_summarizing(limit: int = 5) -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT id, job_url, title, company_name, full_description_text, api_provided_description
            FROM jobs
            WHERE is_relevant_to_criteria = TRUE AND llm_summary IS NULL
            ORDER BY date_fetched DESC LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"❌ ERROR get_jobs_for_summarizing: {e}")
        return []
    finally:
        conn.close()


def update_job_summary(job_url: str, summary_text: str, model_used: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE jobs SET llm_summary = ?, summarizer_model_used = ? WHERE job_url = ?
        ''', (summary_text, model_used, job_url))
        conn.commit()
    except Exception as e:
        print(f"❌ ERROR update_job_summary: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    print("--- Running BittyScout DB Init ---")
    print(f"Database Path: {DB_PATH}")
    create_jobs_table_if_not_exist()
