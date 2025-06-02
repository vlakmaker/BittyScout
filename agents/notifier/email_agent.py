# agents/notifier/email_agent.py

import yagmail
import os

class EmailAgent:
    def __init__(self):
        self.sender = os.getenv("GMAIL_USER")
        self.receiver = os.getenv("RECEIVER_EMAIL")
        self.password = os.getenv("GMAIL_APP_PASSWORD")
        self.subject = "🎯 BittyScout: New AI Jobs for You"

        if not all([self.sender, self.receiver, self.password]):
            raise ValueError("Missing email configuration in .env")

        self.yag = yagmail.SMTP(self.sender, self.password)

    def format_jobs(self, jobs):
        lines = []
        for i, job in enumerate(jobs, 1):
            lines.append(f"{i}. {job['title']} at {job['company']}")
            lines.append(f"   📍 {job.get('location', 'N/A')}")
            lines.append(f"   🔗 {job['url']}")
            lines.append("")  # spacing
        return "\n".join(lines)

    def send_email(self, jobs):
        if not jobs:
            print("📭 EmailAgent: No new jobs to email.")
            return

        body = self.format_jobs(jobs)
        self.yag.send(to=self.receiver, subject=self.subject, contents=body)
        print(f"📧 EmailAgent: Sent {len(jobs)} jobs to {self.receiver}")
