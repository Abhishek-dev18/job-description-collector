import os
import logging
from datetime import datetime
import requests

import pandas as pd
from jobspy import scrape_jobs
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ------------------------ CONFIGURATION ------------------------

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "google-creds.json")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "1Hof8HBclectKVqk6LL7e5OngRj2Q_TuGSRcQ8DUKYZY")
SHEET_RANGE = 'Sheet1!A1'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Valid job site names as per JobSpy
JOB_SITES = ["linkedin", "indeed"]  # Keeping only stable ones
SEARCH_TERM = "software engineer intern"
GOOGLE_SEARCH_TERM = "software engineer intern jobs near India since yesterday"
LOCATION = "India"
RESULTS_WANTED = 100

# ------------------------ LOGGING SETUP ------------------------

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ------------------------ JOB FETCH FUNCTIONS ------------------------

def fetch_jobspy_jobs() -> pd.DataFrame:
    all_jobs = []
    for site in JOB_SITES:
        try:
            logging.info(f"Scraping site: {site}")
            jobs_df = scrape_jobs(
                site_name=[site],
                search_term=SEARCH_TERM,
                google_search_term=GOOGLE_SEARCH_TERM,
                location=LOCATION,
                results_wanted=RESULTS_WANTED,
                linkedin_fetch_description=True,
                country_indeed="India",
                hours_old=72
            )
            jobs_df['source'] = site
            all_jobs.append(jobs_df)
        except Exception as e:
            logging.warning(f"Failed to fetch from {site}: {e}")

    if all_jobs:
        combined = pd.concat(all_jobs, ignore_index=True)
        logging.info(f"Fetched {len(combined)} jobs from JobSpy")
        return combined
    else:
        logging.warning("No jobs fetched from JobSpy sites.")
        return pd.DataFrame()

def fetch_remotive_jobs() -> pd.DataFrame:
    try:
        logging.info("Fetching jobs from Remotive API...")
        response = requests.get("https://remotive.io/api/remote-jobs")
        jobs = response.json().get("jobs", [])
        df = pd.DataFrame(jobs)
        df['source'] = 'remotive'

        columns = ['title', 'company_name', 'category', 'job_type', 'publication_date', 'url', 'description', 'source']
        df = df[columns]
        logging.info(f"Fetched {len(df)} jobs from Remotive")
        return df
    except Exception as e:
        logging.warning(f"Failed to fetch from Remotive: {e}")
        return pd.DataFrame()

# ------------------------ SHEET UPLOAD ------------------------

def append_to_sheet(df: pd.DataFrame):
    try:
        logging.info("Appending data to Google Sheet...")
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)

        df = df.fillna("").astype(str)
        df['date_fetched'] = datetime.now().strftime("%Y-%m-%d")

        values = [df.columns.tolist()] + df.values.tolist()
        body = {'values': values}

        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_RANGE,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()

        updated_rows = result.get('updates', {}).get('updatedRows', 0)
        logging.info(f"Successfully appended {updated_rows} rows.")
    except Exception as e:
        logging.error(f"Failed to append to Google Sheets: {e}")
        raise

# ------------------------ MAIN ENTRY POINT ------------------------

def main():
    try:
        jobspy_df = fetch_jobspy_jobs()
        remotive_df = fetch_remotive_jobs()

        combined_df = pd.concat([jobspy_df, remotive_df], ignore_index=True)

        if not combined_df.empty:
            append_to_sheet(combined_df)
        else:
            logging.warning("No jobs fetched from any source. Nothing to upload.")
    except Exception as e:
        logging.critical(f"Job run failed: {e}")

if __name__ == "__main__":
    main()
