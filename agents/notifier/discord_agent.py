import os
import requests

class DiscordAgent:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        if not self.webhook_url:
            raise ValueError("Missing DISCORD_WEBHOOK_URL in .env")

    def format_job_embeds(self, jobs):
        embeds = []
        for i, job in enumerate(jobs, 1):
            embed = {
                "title": f"{i}. {job['title']} at {job['company']}",
                "description": f"📍 {job.get('location', 'N/A')}\n[🔗 Apply here]({job['url']})",
                "color": 0x00AEEF,  # Light blue BittyScout brand
            }
            embeds.append(embed)
        return embeds

    def send_job_digest(self, jobs):
        if not jobs:
            print("🤖 DiscordAgent: No new jobs to send.")
            return

        summary = {
            "username": "BittyBot",
            "content": f"📬 **BittyScout Digest — {len(jobs)} New Job{'s' if len(jobs) != 1 else ''}**",
            "embeds": self.format_job_embeds(jobs)
        }

        response = requests.post(self.webhook_url, json=summary)
        if response.status_code != 204:
            print(f"❌ DiscordAgent: Failed to send message — {response.status_code}")
            print(response.text)
        else:
            print(f"✅ DiscordAgent: Sent {len(jobs)} jobs to Discord.")
