# MDB Agent

**Intelligent MDB Agent** is a web application that assists a **Moderated Discussion Board (MDB)** for courses. It filters non-academic student messages, matches questions to instructor **PDF handouts** using NLP, and stores queries and answers in a **SQLite** database.

## Features

- Role-based access: **student**, **instructor**, and **admin**
- PDF handout upload with text extraction
- Academic vs. non-academic query filtering with optional logging
- Keyword extraction (KeyBERT) and semantic matching (sentence-transformers) against handout content
- Query history API and dashboards for each role

## Tech stack

- **Backend:** Python 3, Flask, Flask-SQLAlchemy
- **Database:** SQLite (`mdb.db`, created on first run)
- **NLP:** PyPDF2, KeyBERT, sentence-transformers, spaCy (see `requirements.txt`)

## Project layout

```
MDB-Agent/
  app.py              # Flask app and routes
  nlp_utils/          # PDF, filter, keywords, semantic search
  templates/          # HTML dashboards and auth pages
  document/           # Product spec (goal, execution plan)
  requirements.txt
```

## Setup

1. **Create a virtual environment** (recommended):

   ```bash
   cd MDB-Agent
   python -m venv .venv
   .venv\Scripts\activate
   ```

   On macOS/Linux: `source .venv/bin/activate`

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   First run may download embedding models (sentence-transformers / KeyBERT); allow time and network access.

3. **Run the app:**

   ```bash
   python app.py
   ```

   The server starts in debug mode on **http://127.0.0.1:5001** (see `app.py`).

On Windows you can also double-click `Start App.bat` from the `MDB-Agent` folder after activating your environment.

## Default admin (development)

The app seeds a default admin user on first database init (see `init_db()` in `app.py`). **Change or remove this account in production** and use a strong `secret_key` instead of the value hard-coded for development.

## API-style routes (summary)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/upload_handout` | Upload PDF handout |
| POST | `/analyze_query` | Process a student query |
| GET | `/history` | Past queries and responses |

Full behavior and data model are described in `MDB-Agent/document/goal.md`.

## License

No license file is included in this repository; add one if you plan to distribute the project.
