import os
import sys
import requests
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

load_dotenv()

try:
    from utils.db_utils import get_new_relevant_jobs, mark_jobs_as_notified
except ImportError:
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from utils.db_utils import get_new_relevant_jobs, mark_jobs_as_notified


class NotifierAgent:
    def __init__(self):
        self.brevo_api_key = os.getenv("BREVO_API_KEY")
        self.sender_email = os.getenv("EMAIL_SENDER_EMAIL")
        self.sender_name = os.getenv("EMAIL_SENDER_NAME", "BittyScout")
        self.recipient_email = os.getenv("EMAIL_RECIPIENT_EMAIL")

        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)

    def _render_html_digest(self, jobs: list, stats: dict) -> str:
        template = self.jinja_env.get_template('job_digest.html')
        return template.render(
            date=datetime.now().strftime('%B %d, %Y'),
            jobs=jobs,
            top_jobs=jobs[:3],
            other_jobs=jobs[3:],
            stats=stats
        )

    def _send_email_via_brevo(self, html_content: str, subject: str):
        if not all([self.brevo_api_key, self.sender_email, self.recipient_email]):
            print("⚠️ Email credentials not fully configured in .env. Skipping email sending.")
            return False

        payload = {
            "sender": {"email": self.sender_email, "name": self.sender_name},
            "to": [{"email": self.recipient_email}],
            "subject": subject,
            "htmlContent": html_content
        }
        headers = {
            "accept": "application/json",
            "api-key": self.brevo_api_key,
            "content-type": "application/json"
        }

        try:
            response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
            response.raise_for_status()
            print(f"✅ Email sent successfully to {self.recipient_email}!")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send email via Brevo: {e}")
            print(f"   Response Body: {e.response.text if e.response else 'N/A'}")
            return False

    def _notify_via_email(self, jobs, stats):
        html_content = self._render_html_digest(jobs, stats)
        subject = f"🐾 BittyScout Job Digest - {len(jobs)} New Roles ({datetime.now().strftime('%Y-%m-%d')})"
        if self._send_email_via_brevo(html_content, subject):
            self._mark_as_notified(jobs)

    def _notify_via_console(self, jobs, stats):
        html_content = self._render_html_digest(jobs, stats)
        print("--- Displaying Console Digest ---")
        print(html_content)

    def _notify_via_discord(self, jobs):
        from agents.notifier.discord_agent import DiscordAgent
        discord_agent = DiscordAgent()
        discord_agent.send_job_digest(jobs)
        self._mark_as_notified(jobs)

    def _mark_as_notified(self, jobs):
        job_urls = [job['job_url'] for job in jobs]
        mark_jobs_as_notified(job_urls)
        print(f"Marked {len(job_urls)} jobs as notified in the database.")

    def run(self, channel="console"):
        print("\n--- 📣 Starting Notifier Agent ---")
        jobs_to_notify = get_new_relevant_jobs()

        if not jobs_to_notify:
            print("✅ No new relevant jobs found to notify about.")
            print("--- Notifier Agent Complete ---")
            return

        print(f" Found {len(jobs_to_notify)} new relevant jobs to send.")
        stats = {
            "newly_added": "N/A",
            "sources_queried": 4,
            "passed_triage": "N/A"
        }

        if channel == "email":
            self._notify_via_email(jobs_to_notify, stats)
        elif channel == "console":
            self._notify_via_console(jobs_to_notify, stats)
        elif channel == "discord":
            self._notify_via_discord(jobs_to_notify)
        else:
            print(f"❌ Unknown channel '{channel}'. Please choose from: email, console, discord.")

        print("--- Notifier Agent Complete ---")
