# ETHGlobal Project Crawler

This repository provides Python scripts to **scrape and download projects from [ETHGlobal](https://ethglobal.com/)**.  
The scripts bypass ETHGlobal’s limited search functionality, enabling **comprehensive offline access** to project data for exploration, analysis, or integration.

## Features

- **Complete project listing:** Crawls all project listings from ETHGlobal and saves them to a single CSV file.  
- **Detailed project extraction:** Fetches individual project pages and stores structured details (description, tech stack, awards, links, etc.) as separate CSV files.  
- **Resumable execution:** Automatically resumes from the last processed project if interrupted.  
- **Rate-limit handling:** Detects and waits on HTTP 429 responses to avoid bans.  
- **Duplicate cleanup:** Removes sequential duplicate entries in the final project list.  

## Files

### `ethglobal_crawler.py`
Scrapes the ETHGlobal `/showcase` pages:

- Iterates through all paginated project listings.  
- Extracts **name, short description, and project URL** for each project.  
- Appends results to `ethglobal_projects.csv`, creating it if missing.  
- Handles HTTP rate limits gracefully and deduplicates sequential duplicates at the end.  
- Configurable **rate-limiting** (delay between requests, retry on HTTP 429).  

### `ethglobal_crawler_detail.py`
Fetches detailed information for each project listed in `ethglobal_projects.csv`:

- Visits each project page and extracts:
  - **Name** and **short description**.  
  - **Live demo** and **source code URLs** (if available).  
  - **Full project description** and **“How it’s Made”** section.  
  - **Creation hackathon link** and **awards** (ETHGlobal or track prizes).  
- Saves each project’s details to a **separate CSV** in `project_details/`.  
- Supports **resume-on-crash** (continues from the last saved project).  
- Logs errors to `project_details/error_log.txt` when saving fails.  

## Setup

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate   # On Linux/macOS
venv\Scripts\activate      # On Windows

# Install dependencies
pip install requests beautifulsoup4 pandas
```

## Usage

```bash
# 1. Fetch the general list of projects (creates ethglobal_projects.csv)
python ethglobal_crawler.py

# 2. Fetch detailed data for each project (saves CSVs to project_details/)
python ethglobal_crawler_detail.py
```

## Output

- `ethglobal_projects.csv` – All ETHGlobal projects with **name, description, URL**.  
- `project_details/` – One CSV per project with **full metadata**.  
- `project_details/error_log.txt` – Records any file save errors.  

---

This setup provides **structured, offline-accessible ETHGlobal hackathon data**, ready for analysis or integration into your own tools.
