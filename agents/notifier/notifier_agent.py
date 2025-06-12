# agents/notifier/notifier_agent.py
import os
import sys
import requests
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

try:
    from utils.db_utils import get_new_relevant_jobs, mark_jobs_as_notified
except ImportError:
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if PROJECT_ROOT not in sys.path: sys.path.insert(0, PROJECT_ROOT)
    from utils.db_utils import get_new_relevant_jobs, mark_jobs_as_notified

class NotifierAgent:
    def __init__(self):
        """Initializes the NotifierAgent with Brevo email credentials."""
        self.brevo_api_key = os.getenv("BREVO_API_KEY")
        self.sender_email = os.getenv("EMAIL_SENDER_EMAIL")
        self.sender_name = os.getenv("EMAIL_SENDER_NAME", "BittyScout")
        self.recipient_email = os.getenv("EMAIL_RECIPIENT_EMAIL")
        
        # Setup Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)

    def _render_html_digest(self, jobs: list, stats: dict) -> str:
        """Renders the HTML email using the Jinja2 template."""
        template = self.jinja_env.get_template('job_digest.html')
        
        # Split jobs for the template: e.g., top 3 and the rest
        top_jobs = jobs[:3]
        other_jobs = jobs[3:]
        
        return template.render(
            date=datetime.now().strftime('%B %d, %Y'),
            jobs=jobs,
            top_jobs=top_jobs,
            other_jobs=other_jobs,
            stats=stats
        )

    def _send_email_via_brevo(self, html_content: str, subject: str):
        """Sends the rendered HTML email via the Brevo API."""
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

    def run(self, channel="console"):
        print("\n--- 📣 Starting Notifier Agent ---")
        jobs_to_notify = get_new_relevant_jobs()
        
        if not jobs_to_notify:
            print("✅ No new relevant jobs found to notify about.")
            print("--- Notifier Agent Complete ---")
            return

        print(f" Found {len(jobs_to_notify)} new relevant jobs to send.")
        
        # These stats are just for the email template, you can make them more dynamic
        stats = {
            "newly_added": "N/A", # Could be fetched from a log or DB count
            "sources_queried": 4, # Hardcoded for now
            "passed_triage": "N/A"
        }
        
        html_content = self._render_html_digest(jobs_to_notify, stats)
        
        if channel == "email":
            subject = f"🐾 BittyScout Job Digest - {len(jobs_to_notify)} New Roles ({datetime.now().strftime('%Y-%m-%d')})"
            email_sent = self._send_email_via_brevo(html_content, subject)
            
            # Only mark jobs as notified if the email was sent successfully
            if email_sent:
                job_urls = [job['job_url'] for job in jobs_to_notify]
                mark_jobs_as_notified(job_urls)
                print(f"Marked {len(job_urls)} jobs as notified in the database.")

        elif channel == "console":
            print("--- Displaying Console Digest (HTML will not render fully) ---")
            print(html_content)
        
        print("--- Notifier Agent Complete ---")
