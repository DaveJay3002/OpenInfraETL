# Open Infra Project Scraper & API

This project scrapes real estate project data from the Odisha RERA website, stores it in a PostgreSQL database, and exposes a FastAPI backend to trigger scraping and fetch stored projects.

---

## Features

- Multi-page scraping of RERA project listings using Selenium & BeautifulSoup
- SQLAlchemy ORM for PostgreSQL data persistence with duplicate prevention
- FastAPI endpoints to:
  - Trigger project scraping on demand
  - Fetch all stored projects as JSON
- Configurable Chrome & ChromeDriver paths via environment variables
- Clean, modular codebase designed for easy extension and deployment

---

## Tech Stack

- Python 3.12+
- Selenium & BeautifulSoup for scraping
- SQLAlchemy ORM + PostgreSQL
- FastAPI with Uvicorn server
- Pydantic v2 for request/response models
- dotenv for environment variable management

---

## Getting Started

### Prerequisites

- PostgreSQL database up and running
- Chrome browser and compatible ChromeDriver installed
- Python 3.12+ installed

### Setup

1. Clone the repo:

   ```bash
   git clone <repo-url>
   cd <repo-directory>
    ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and update with your settings:

   ```env
   DB_URL=postgresql://user:password@localhost:5432/yourdb
   CHROME_BINARY_PATH=/path/to/chrome
   CHROMEDRIVER_PATH=/path/to/chromedriver
   ```

5. Initialize database tables:

   ```bash
   python db/init_db.py
   ```

6. Run the FastAPI server:

   ```bash
   uvicorn api.main:app --reload
   ```

---

## Usage

* **Trigger scraping:**
  Send a GET request to `/scrape` to start scraping multiple pages and save to DB.

  ```bash
  curl http://localhost:8000/scrape
  ```

* **Fetch all projects:**
  Send a GET request to `/projects` to retrieve all scraped projects in JSON.

  ```bash
  curl http://localhost:8000/projects
  ```

* Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API docs.

---

## Project Structure

```
.
├── api
│   └── main.py           # FastAPI app with routes
├── db
│   ├── models.py         # SQLAlchemy models
│   ├── database.py       # DB engine and session setup
│   └── init_db.py        # DB table initialization
├── scraper
│   └── scrape_projects.py # Selenium scraper logic
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
└── README.md
```

---

## Notes

* Chrome and ChromeDriver paths must be set correctly in `.env` for scraper to work.
* Scraper runs headless with options to support Linux server environments.
* The scraper handles pagination and prevents duplicates by checking `rera_no`.
* API responses use Pydantic models configured for SQLAlchemy ORM compatibility (Pydantic v2).

---

