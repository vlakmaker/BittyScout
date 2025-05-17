## 📁 Root Files

| File | Purpose |
| --- | --- |
| `main.py` | The **entry point** of the app. It will initialize the manager agent and trigger the flow. Later, you could add CLI args or a FastAPI interface here. |
| `README.md` | The **project overview**, goals, agent descriptions, and how to run it. You’ll update this as BittyScout evolves. |
| `requirements.txt` | Python dependencies. Start with basics: `requests`, `beautifulsoup4`, `openai`, `pydantic`, etc. |

---

## 📁 `agents/`

This is your **core agent system**, split by responsibility. Each subfolder contains one *agent module* (its class, prompt templates, and utilities if needed).

| Folder | Contents | Purpose |
| --- | --- | --- |
| `manager/` | `manager_agent.py` | Orchestrates the flow. Decides which agents run and in what order. Think of it like the conductor of the whole system. |
| `scraper/` | `scraper_agent.py` | Gathers raw job data from the web. You'll write functions to scrape or call job board APIs. |
| `parser/` | `parser_agent.py` | Cleans up messy HTML or API responses into structured Python dicts or `Job` objects (with fields like `title`, `location`, `tags`, etc). |
| `scorer/` | `scorer_agent.py` | Evaluates each job against your preferences (GenAI, strategy, remote). Uses rule-based logic or LLMs. |
| `summarizer/` | `summarizer_agent.py` | Generates short summaries or highlights for each job. This is where prompt engineering comes in. |
| `memory/` | `memory_agent.py` | Keeps track of already-seen jobs, stores job history, and will later track feedback or application status. |
| `output/` | `output_agent.py` | Converts the final result into Markdown, Notion-compatible blocks, or frontend-ready JSON. It formats and "presents" the findings. |

---

## 📁 `config/`

Where you’ll define things like:

- Which job boards to scrape
- Scoring preferences (e.g. `remote = +2`, `consulting = +1`, etc.)
- LLM provider settings (e.g. API key, model, temperature)

**Key file to add soon:** `bittyscout_config.yaml`

---

## 📁 `data/`

Stores:

- Scraped raw data (e.g. job listings)
- Processed job objects
- Output files (e.g. a weekly digest in Markdown)
- Optionally: your seen jobs cache (`seen_jobs.json`)

You could keep this simple flat files or connect it to SQLite later.

---

## 📁 `tests/`

Unit tests per agent. You’ll write tests like:

- `test_scraper_remoteok.py`: does it return valid jobs?
- `test_parser_cleanup.py`: does it correctly extract the job title?
- `test_scorer_matrix.py`: does scoring match your criteria?

Start simple with `pytest` or `unittest`.

---

## 📁 `utils/`

Any shared functions used across agents:

- `text_cleaner.py`: for removing HTML or junk
- `job_model.py`: defines a `Job` class or dataclass
- `logging_utils.py`: for colored console logs or structured debugging
- `llm_utils.py`: generic wrappers for OpenAI/OpenRouter requests

This keeps your agent files clean and focused.

---

## 🧱 Summary Diagram

```
lua
CopyEdit
main.py
└── agents/
    ├── manager/
    ├── scraper/
    ├── parser/
    ├── scorer/
    ├── summarizer/
    ├── memory/
    └── output/
config/
data/
tests/
utils/

```