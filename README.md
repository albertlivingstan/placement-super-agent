# Placement Super Agent 2027

Free educational multi-agent-style job dashboard built with Flask and SQLite.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. On Windows use `.venv\Scripts\activate`.

## Features
- Job discovery: manually add official job links; 3 sample jobs are NOT LIVE.
- Eligibility: graduation year and CGPA checks.
- Resume match: exact comma-separated keyword matching, with explainable percentage.
- Preparation: built-in Python, SQL, JavaScript and general interview questions.
- Tracking: save application status in SQLite.

## Important limitations
This is a local MVP, not a live autonomous job scraper or LLM system. Job listings must be verified with the employer. This app has no accounts or CSRF protection and must NOT be deployed publicly as-is. For the free Superagent security workflow, publish the code (not the database) to GitHub, connect the repository at https://superagent.sh/ and review PR security scans. Superagent is a security scanning product, not the orchestration runtime of this app.
