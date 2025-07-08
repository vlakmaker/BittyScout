# FILE: ~/BittyScout/agents/notifier/discord_agent.py

import os
import requests

class DiscordAgent:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        if not self.webhook_url:
            raise ValueError("Missing DISCORD_WEBHOOK_URL in .env")

    # --- THIS IS THE MISSING METHOD ---
    def format_job_embeds(self, jobs):
        """
        Takes a list of job dictionaries and formats them into Discord embeds.
        """
        embeds = []
        for i, job in enumerate(jobs[:10], 1): # Limit to 10 embeds per Discord message
            # Safely get the URL to prevent crashes
            job_url = job.get('job_url', '#')
            
            embed = {
                "title": f"{i}. {job.get('title', 'N/A')} at {job.get('company_name', 'N/A')}",
                "description": f"📍 {job.get('location', 'N/A')}\n[🔗 Apply here]({job_url})",
                "color": 0x00AEEF,  # BittyScout blue
            }
            embeds.append(embed)
        return embeds

    def send_job_digest(self, jobs):
        """
        Takes a list of jobs, formats them, and sends them to the Discord webhook.
        """
        if not jobs:
            print("🤖 DiscordAgent: No new jobs to send.")
            return

        summary = {
            "username": "BittyBot",
            "content": f"📬 **BittyScout Digest — {len(jobs)} New Job{'s' if len(jobs) != 1 else ''}**",
            "embeds": self.format_job_embeds(jobs) # This call will now work
        }

        print("🤖 DiscordAgent: Attempting to send message to Discord webhook...")
        try:
            response = requests.post(self.webhook_url, json=summary, timeout=10)
            response.raise_for_status()
            print(f"✅ DiscordAgent: Successfully sent {len(jobs)} jobs to Discord (Status: {response.status_code}).")
        except requests.exceptions.RequestException as e:
            print(f"❌ DiscordAgent: CRITICAL FAILURE sending message to Discord.")
            print(f"   Error: {e}")
            if e.response is not None:
                print(f"   Response Status Code: {e.response.status_code}")
                print(f"   Response Body from Discord: {e.response.text}")