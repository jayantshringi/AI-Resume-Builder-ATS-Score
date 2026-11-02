# AI Resume Builder & ATS Score

A Flask full-stack starter project with a responsive frontend, rule-based ATS estimate, resume builder, PDF/DOCX/TXT extraction, account registration, analysis history, and a contact/complaint form that saves messages in SQLite and attempts email notifications to both configured contact addresses.

## Features

- Responsive blue/cyan landing page and navigation.
- Resume form with browser print / Save as PDF.
- Dynamic rule-based ATS estimate with eight weighted factors.
- Matched/missing keywords and actionable suggestions.
- PDF, DOCX and TXT text extraction.
- Contact/suggestion/complaint form stored in SQLite.
- SMTP notifications to `mohitki7780264@gmail.com` and `adityasing9508@gmail.com`.
- Login, registration, password hashing, and per-user analysis history.
- Unit tests for the scoring engine and text parser.

## Requirements

- Python 3.10 or newer recommended.
- Internet is not required for the core website after dependencies are installed.
- No paid AI API is required.
- Text-based PDFs are supported. Scanned PDFs and image resumes need OCR, which is not included in this starter build.

## Setup (Windows / VS Code)

1. Extract the ZIP.
2. Open the extracted `AI-Resume-ATS` folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal and activate again. Or use Command Prompt:
   `.venv\Scripts\activate.bat`

5. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

6. Copy `.env.example` to `.env`. Update `SECRET_KEY`. The site works without SMTP, but email notifications won't send until SMTP is configured.

7. Start the website:

   ```powershell
   python app.py
   ```

8. Open `http://127.0.0.1:5000` in your browser.

## Email setup

The website saves each contact message to SQLite first. It then attempts to send one notification email addressed to both contact addresses. If SMTP is not configured or email delivery fails, the message remains saved and the website displays a warning.

For Gmail SMTP:
1. Use a Gmail account you control as the sender (`SMTP_USERNAME` and `MAIL_FROM`).
2. Enable two-step verification on that sender account.
3. Create a Google App Password from your Google Account security settings, if available for your account.
4. Put the App Password in `SMTP_PASSWORD`. Do not use your normal Gmail password.
5. Keep `.env` private and never commit it.
6. Restart Flask and submit a test contact message.

The two contact addresses are recipients, not necessarily the sending account. The sender account must be authorized to send mail. Check spam folders and sender security settings if messages do not arrive.

## How the ATS score works

The scoring engine calculates an estimate from eight weighted factors:
- Keyword match: 25%
- Job title and skills: 15%
- Resume structure: 10%
- Formatting/readability heuristics: 10%
- Contact details: 5%
- Content quality: 10%
- Education and experience: 15%
- Length and consistency: 10%

The result is calculated from each resume and job description; it is not fixed or random. It uses standard Python text processing and a known-skill dictionary. It does not call a paid AI API and cannot reproduce the proprietary scoring rules of every employer ATS.

## Run tests

```powershell
python -m pytest -q
```

## Database and privacy

SQLite database file is created automatically at `database/app.db`. The contact form stores name, email, category, subject, message, timestamp and email delivery status. Analysis history stores the account ID (when logged in), job title, score and timestamp. Resume uploads are deleted after processing.

Before public deployment, add CSRF protection, rate limiting, production-grade secret management, secure HTTPS, database backup/deletion policy, and stronger abuse protection. Do not use Flask's development server or `debug=True` in production.

## Important limitations

- Formatting checks are heuristics based on extracted text; the program cannot reliably detect every column, icon, font or visual alignment issue.
- OCR for scanned documents is not included.
- The resume builder preview is printable through the browser; it does not create a server-side DOCX file.
- Email delivery requires valid SMTP credentials.
