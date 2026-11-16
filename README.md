# FocusLab — Student Digital Habits Survey

**FocusLab** is a small, privacy-conscious data collection and analytics app built with Python, Streamlit, Plotly and Supabase.

The project explores how students' smartphone habits, notification interruptions and study routines relate to their self-reported ability to concentrate.

> This is an educational survey, not a clinical or scientifically validated attention assessment.

## Live demo

Add your deployed Streamlit Community Cloud URL here after deployment.

## Features

- Anonymous questionnaire with validation and optional free-text feedback.
- Persistent response storage in Supabase (PostgreSQL).
- Interactive charts for notification frequency and daily smartphone screen time.
- Aggregate-only public analytics: individual submissions and free-text comments are not exposed by the dashboard.
- Existing responses from the earlier Russian-language version remain compatible with the aggregate statistics function.
- Responsive Streamlit layout and CSV-free public dashboard to reduce unnecessary exposure of participant data.

## Tech stack

- Python 3.10+
- Streamlit
- pandas
- Plotly
- Supabase Python client
- PostgreSQL / JSONB / Row Level Security

## Run locally

1. Clone this repository:

   ```bash
   git clone https://github.com/gafinmarsel-ops/-1-5.git
   cd -1-5
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   # macOS / Linux
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Create `.streamlit/secrets.toml`:

   ```toml
   SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
   SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_OR_PUBLISHABLE_KEY"
   ```

   Use the project's public anon/publishable key. **Never put a service-role key in this app or commit secrets to Git.**

5. Configure the database using [supabase/setup.sql](supabase/setup.sql) in the Supabase SQL Editor.

6. Start the app:

   ```bash
   streamlit run app.py
   ```

## Database setup and privacy

The app expects a table named `public.survey_responses` with an `answers` JSONB column. The SQL setup script:

- creates the table if it does not exist;
- enables Row Level Security;
- permits anonymous submissions only;
- creates a PostgreSQL function that returns aggregate counts and averages;
- grants the public app permission to execute that aggregate function, without granting it permission to read individual survey rows.

The dashboard deliberately does not select raw submissions. Review the SQL and your Supabase policies before collecting real participant data. Do not collect names, email addresses, phone numbers or other identifying details.

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub.
2. Create a new app in Streamlit Community Cloud and select this repository.
3. Set the main file path to `app.py`.
4. Add `SUPABASE_URL` and `SUPABASE_ANON_KEY` in the app's Secrets settings.
5. Deploy and test a submission and the aggregate dashboard.

## Project structure

```text
.
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
└── supabase/
    └── setup.sql
```

## Roadmap

- Add automated tests for response validation and analytics transformations.
- Add localization support.
- Add a documented research methodology and limitations section.
- Add a reproducible sample dataset for development and screenshots.

## Author

Marcel Gafin — student developer.

If you use or adapt this project, please keep participant privacy and the limitations of self-reported survey data in mind.
