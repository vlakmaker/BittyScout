# 🤖 BittyScout

**BittyScout** is a Python-based job discovery agent that automates the process of finding relevant AI jobs based on your personal preferences and career goals. It scrapes multiple job platforms, filters them using custom criteria, ranks them based on similarity to your ideal role, and sends you a daily email summary of the best matches.

---

## 📌 Features

- 🔍 **Scrapes** job listings from Recruitee, Lever, and Workable boards
- 🧲 **Matches** jobs to your preferences using keywords and location criteria
- 🧠 **Scores** relevance using semantic similarity with a SentenceTransformer
- 📝 **Summarizes** job listings to make them easier to digest
- 📧 **Emails** the top job matches to your inbox
- 💾 **Caches** previously sent jobs to avoid duplicates

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourname/bittyscout.git
cd bittyscout

```

### 2. Set Up the Environment

```bash
conda create -n bittyscout python=3.10
conda activate bittyscout
pip install -r requirements.txt

```

### 3. Configure Environment Variables
Create a .env file in the root folder:

pip install -r requirements.txt
3. Configure Environment Variables
Create a .env file in the root folder:

GMAIL_USER=your.email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
RECEIVER_EMAIL=recipient.email@example.com
💡 Use an App Password if 2FA is enabled on your Gmail account.

### ⚙️ Configuration
#### Matcher Criteria
Located at: config/matcher_config.json

``` json
{
"keywords": ["AI", "Product", "Strategy"],
"locations": ["remote", "hybrid", "antwerp"],
"remote_days_max": 3
}

``` 

Adjust these to match your job preferences.

### 🧪 Running the Script
``` bash
python [main.py](http://main.py/)

``` 
This will run the entire flow: scrape → filter → score → summarize → output → email.

### 🖥 Deployment Suggestion
To run BittyScout daily on a remote server:

1. Copy the project to your server
2. Create a cron job:

``` bash
crontab -e

```
Add the line:

```bash
0 9 * * * /path/to/miniconda3/envs/bittyscout/bin/python /path/to/bittyscout/main.py
```

### 🗃 Directory Structure
```lua
bittyscout/
├── agents/
│   ├── matcher/
│   ├── scorer/
│   ├── scraper/
│   ├── summarizer/
│   ├── notifier/
│   └── output/
├── config/
├── utils/
├── outputs/
├── [main.py](http://main.py/)
└── [README.md](http://readme.md/)

```

### 🧠 Powered By
- sentence-transformers (all-MiniLM-L6-v2)
- yagmail
- requests, json, dotenv

### 📬 Future Ideas
- ✅ Add support for more job boards (e.g., Greenhouse, SmartRecruiters)
- 📊 Add analytics/report generation
- 🧠 Personalization via feedback loop
- 🌐 Simple Web UI or CLI dashboard

### 👤 Author
Built with ❤️ by Vera Lakmaker + Bitty (GPT-4o).
Feedback or feature ideas? Let’s connect!