# Job Description Collector

This project automates the daily collection of job descriptions from multiple platforms and uploads them to Google Sheets.

---

## Features

- Fetches job listings (including full job descriptions) from LinkedIn, Indeed, Glassdoor, Google Jobs, ZipRecruiter, Naukri, Remotive, and more using JobSpy.
- Appends job data daily to a specified Google Sheet.
- Fully automated via GitHub Actions workflow scheduled to run once daily.

---

## Setup Instructions

### 1. Google Sheets API

- Create a Google Cloud project and enable the Google Sheets API.
- Create a Service Account with **Editor** access to your Google Sheet.
- Download the JSON credentials file.
- Share your Google Sheet with the Service Account email.

### 2. GitHub Secrets

Add the following secrets in your GitHub repository settings:

- `GOOGLE_CREDENTIALS_JSON`: Contents of the Service Account JSON file.
- `SPREADSHEET_ID`: Your Google Sheet ID (from the sheet URL).

### 3. Repository Structure

<pre> <code>``` job-description-collector/ │ ├── job_fetcher.py ├── .github/ │ └── workflows/ │ └── daily-job-fetch.yml ├── README.md ```</code> </pre>


