# BittyScout 🧠🔍

BittyScout is a modular, agentic, AI-powered job discovery pipeline. It scrapes job listings from multiple platforms, uses LLMs to filter them for relevance against your personal criteria, and delivers a clean digest of new, interesting opportunities directly to you.

This project is now fully containerized using Docker and designed for automated, scheduled execution via n8n.

# ✨ Features

- **Multi-Source Scraping**: Ingests job listings from platforms like Recruitee, Lever, Greenhouse, Adzuna, and more.
- **AI-Powered Filtering**: Employs a two-stage LLM process (via Groq and OpenRouter) to triage and deeply analyze jobs for relevance.
- **Automated Pipeline**: The entire scrape -> filter -> notify pipeline can be triggered via a simple API call.
- **Containerized & Scalable**: Runs as a set of coordinated Docker containers, managed by Docker Compose, making deployment and management simple.
- **Asynchronous Job Handling**: Uses a Redis/Celery queue to handle long-running scraping and filtering tasks in the background without blocking.
- **Multiple Notification Channels**: Delivers digests via Discord, email (Brevo), or directly to the console.

# 🔧 Tech Stack

- **Application**: Python, FastAPI, Celery
- **Database**: SQLite
- **Web Scraping**: requests, beautifulsoup4, playwright
- **AI**: LLM APIs via Groq & OpenRouter
- **Orchestration**:
    - **n8n**: For scheduling and triggering the pipeline.
    - **Docker & Docker Compose**: For containerization.
    - **Traefik**: As a reverse proxy for n8n.
    - **Redis**: As a message broker for background tasks.
- **Hosting**: Hetzner (Linux)

# 📦 Docker-Based Installation & Setup

BittyScout is designed to run as a multi-container Docker application.

### Prerequisites

- Docker and Docker Compose installed on your server.
- A running Traefik container connected to an external Docker network named traefik.
- A running n8n container also connected to the traefik network.

### Configuration

1. **Clone the Repository**:Generated bash
    
    `git clone https://github.com/vlakmaker/BittyScout.git
    cd BittyScout`
    
    Use code [**with caution**](https://support.google.com/legal/answer/13505487).Bash
    
2. **Create .env File**:Generated env
    
    Create a .env file in the BittyScout root directory. This file stores all your secrets and configurations.
    
    `# --- LLM API Keys ---
    OPENROUTER_API_KEY=your_openrouter_key
    GROQ_API_KEY=your_groq_key
    
    # --- Notification Service Keys ---
    BREVO_API_KEY=your_brevo_key
    EMAIL_SENDER_EMAIL=your_verified_brevo_email
    EMAIL_RECIPIENT_EMAIL=your_email_to_receive_digest
    DISCORD_WEBHOOK_URL=your_discord_webhook_url
    
    # --- Database Name ---
    DB_NAME=bittyscout.db
    
    # --- Redis URL (for Celery) ---
    REDIS_URL=redis://bittyscout-redis:6379/0`
    
    Use code [**with caution**](https://support.google.com/legal/answer/13505487).Env
    
3. **Job Sources**:
    
    Ensure config/job_sources.yml exists and is populated with your target companies and search queries.
    
4. **Python Dependencies**:Generated bash
    
    Generate a pip-compatible requirements.txt file from your local environment.
    
    `# From your activated conda environment
    pip freeze > requirements.txt`
    
    Use code [**with caution**](https://support.google.com/legal/answer/13505487).Bash
    
    Ensure celery and redis are included in this file.
    

# 🚀 Running the Application

BittyScout now runs as three coordinated services defined in docker-compose.yml:

- bittyscout-api: The lightweight FastAPI web server that accepts requests.
- bittyscout-worker: The Celery worker that executes the long-running scrape/filter tasks.
- bittyscout-redis: The message queue that connects the API and the worker.

### To Start the Services:

From the BittyScout root directory, run:

Generated bash

`sudo docker-compose up --build -d`

Use code [**with caution**](https://support.google.com/legal/answer/13505487).Bash

This will build the Docker image and start all three services in the background.

### To Stop the Services:

Generated bash

`sudo docker-compose down`

Use code [**with caution**](https://support.google.com/legal/answer/13505487).Bash

# 🤖 Usage with n8n

The primary way to use BittyScout is to trigger its API endpoints from an n8n workflow.

- **API Base URL**: http://bittyscout-api:8000 (This is the internal Docker network address n8n will use).
- **Endpoints**:
    - POST /scrape: Queues a job to scrape all sources.
    - POST /filter: Queues a job to filter all unprocessed listings.
    - POST /notify?channel=discord: Queues a job to send a digest to the specified channel.
    - POST /run: Queues the full scrape -> filter -> notify pipeline as a single task.

An example n8n workflow would be a "Schedule Trigger" that calls the /run endpoint once a day.

### Manual Usage (For Debugging)

You can still run the logic manually by getting a shell inside the running worker container:

Generated bash

`sudo docker exec -it bittyscout-worker /bin/sh

# Now inside the container, you can run commands:
# Note: The main script is now named 'logic.py'
python logic.py scrape --source Greenhouse
python logic.py filter`

Use code [**with caution**](https://support.google.com/legal/answer/13505487).Bash

# 📁 Folder Structure

- agents/: Contains the core logic for the Scraper, Filter, and Notifier agents.
- config/: Holds job_sources.yml and LLM prompts.
- utils/: Database utilities and other helper functions.
- api.py: The FastAPI application code.
- logic.py: The main application entrypoint containing the core pipeline functions (formerly main.py).
- tasks.py: Defines the Celery background tasks.
- Dockerfile: Instructions to build the BittyScout application image.
- docker-compose.yml: Defines and configures the API, worker, and Redis services.
- bittyscout.db: The SQLite database file.

# 💡 Future Roadmap

- Frontend interface for filtered job browsing.
- Tag-based filtering and bookmarking.
- Integration with BittyNews portal.

---

🧠 *Made with curiosity, frustration with job boards, and a stubborn desire to build something useful. From an information geek who's learning as they go.*

📮 **Contact**: Want to build something similar? Find me on [**LinkedIn**](https://www.google.com/url?sa=E&q=your-linkedin-url) or check out [**bittygpt.com**](https://www.google.com/url?sa=E&q=https%3A%2F%2Fwww.bittygpt.com).