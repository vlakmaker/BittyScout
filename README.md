# BittyScout 🧠🔍

BittyScout is a modular, agentic, AI-powered job discovery agent that scrapes job listings from multiple platforms, filters them using LLMs, and delivers a clean email digest of relevant opportunities.

---

## ✨ Features

### ✅ Autonomous Pipeline
BittyScout runs in three stages:
1. **Ingestion:** Scrapes job listings from platforms like Recruitee, Lever, Greenhouse, Adzuna, and Personio.
2. **Processing:** Filters and scores jobs using LLMs via Groq and OpenRouter.
3. **Presentation:** Sends a daily digest of relevant jobs using Brevo.

### 🔧 Tech Stack
- Python + SQLite
- `requests`, `beautifulsoup4`, `feedparser`
- LLM APIs via Groq/OpenRouter
- Email notifications via Brevo
- HTML templating with Jinja2
- Hosted on Hetzner (Linux)

---

## 📦 Installation

```bash
git clone https://github.com/vlakmaker/BittyScout.git
cd BittyScout
python3 -m venv bittyscout
source bittyscout/bin/activate
pip install -r requirements.txt
```

---

## 🔐 Configuration

Create a `.env` file in the root directory:

```
OPENROUTER_API_KEY=your_openrouter_key
GROQ_API_KEY=your_groq_key
BREVO_API_KEY=your_brevo_key
SENDER_EMAIL=your_verified_brevo_email
RECIPIENT_EMAIL=your_email_to_receive_digest
```

Make sure `config/job_sources.yml` exists and lists your target companies.

---

## 🚀 Usage

```bash
# Scrape job boards and store raw jobs
python main.py scrape

# Filter jobs using LLM triage + analysis
python main.py filter

# Send digest of relevant jobs via email
python main.py notify

# Or run all stages at once
python main.py run
```

---

## 📁 Folder Structure

- `scrapers/` – platform-specific job scrapers
- `agents/` – ScraperAgent, FilterAgent, NotifierAgent
- `config/` – job_sources.yml & prompts
- `templates/` – email digest template
- `bittyscout.db` – SQLite database

---

## 💡 Future Roadmap

- Frontend interface for filtered job browsing
- Tag-based filtering and bookmarking
- Integration with BittyNews portal

---

## 🧠 Made With
Curiosity, frustration with job boards, and a stubborn desire to build something useful. From an information geek who's learning as they go.

---

## 📮 Contact
Want to build something similar? DM me on LinkedIn or check out [bittygpt.com](https://bittygpt.com).
