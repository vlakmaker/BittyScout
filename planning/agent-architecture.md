# 🧠 BittyScout – Agent Architecture v1.1

### 🏁 Goal
BittyScout is a multi-agent system designed to **automate job discovery and recommendation** using AI tools and structured workflows. It mirrors the logic of a digital research assistant, tuned for job search, filtering, and feedback-based improvement.

## 🔧 Core Agent Roles

| Agent | Description | Responsibilities | Tools/Skills |
|-------|-------------|------------------|--------------|
| 🎩 Manager Agent | Orchestrator | Triggers the flow, delegates tasks, handles memory checks | FastAPI logic, workflow control |
| 🌐 Scraper Agent | Information gatherer | Pulls job listings from curated job sources | `requests`, `BeautifulSoup`, APIs |
| 🧹 Parser Agent | Cleaner + Structurer | Transforms raw HTML/text into structured job objects | Python parsing, keyword/tag extraction |
| 🧠 Scorer Agent | Evaluator | Ranks jobs based on user-defined priorities (e.g., GenAI, remote, strategic) | LLM or rule-based scoring |
| 📌 Summarizer Agent | Communicator | Generates short summaries + relevance notes for each job | Few-shot prompting, OpenRouter or Mistral |
| 🗃️ Memory Agent | Deduplication / Learning | Checks if a job has already been seen, stores user feedback | JSON/SQLite DB, local caching |
| 📤 Output Agent | Presenter | Displays job recs in Markdown, Notion, or UI-ready format | Markdown, Notion API, future frontend |

## 🧭 Information Flow

```
Trigger (cron or manual)
        ↓
Manager Agent
        ↓
Scraper Agent → Parser Agent
        ↓
Memory Filter (has this job been seen?)
        ↓
Scorer Agent → Summarizer Agent
        ↓
Output Agent (UI, Markdown, Notion)
```

## 🪙 Bitty Points of Intelligence

| Decision Point | Logic |
|----------------|-------|
| When to scrape | Time-based (daily), or triggered |
| How to score | Based on profile-matched criteria (AI-related, strategic, remote, user-defined) |
| What to show | Only jobs not seen before, sorted by score |
| How to summarize | 3 bullets: role, why it's interesting, any red flags |

## 🔁 Future Capabilities (v2.0+)

- 🔄 Feedback loop from user (mark as applied / ignored / interesting)
- 🧠 Preference learning (learn from which jobs you liked or clicked)
- 📨 Notification agent (daily digest via email/Telegram)
- 💬 Ask-Bitty mode (“Find me jobs like that OpenAI one I liked”)

## 🛠️ Deployment Options

| Component | Option |
|----------|--------|
| Backend | FastAPI |
| Agent control | Manual Python routing or LangGraph for multi-agent logic |
| Hosting | Oracle Cloud (Dockerized) |
| Memory | Flat JSON → later SQLite or Vector DB |
| LLMs | OpenRouter / Mistral 7B for scoring and summarization |