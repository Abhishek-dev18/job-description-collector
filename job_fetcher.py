import os
import pandas as pd
from datetime import datetime
from jobspy import scrape_jobs
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Read service account credentials file path from environment variable
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "path_to_your_service_account_credentials.json")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "your_google_sheet_id_here")  # Set as env var in GitHub Secrets or replace here
SHEET_RANGE = 'Sheet1!A1'  # Change if needed

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def append_to_sheet(df: pd.DataFrame):
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    values = [df.columns.values.tolist()] + df.values.tolist()
    body = {'values': values}

    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_RANGE,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    print(f"Appended {result.get('updates').get('updatedRows')} rows to Google Sheet.")

def fetch_jobs():
    jobs_df = scrape_jobs(
        site_name=["linkedin", "indeed", "glassdoor", "google", "ziprecruiter", "naukri", "remotive"],
        search_term="",
        location="",
        results_wanted=100,
        linkedin_fetch_description=True
    )
    return jobs_df

def main():
    print("Fetching jobs...")
    jobs_df = fetch_jobs()
    jobs_df['date_fetched'] = datetime.now().strftime("%Y-%m-%d")
    print(f"Fetched {len(jobs_df)} jobs. Uploading to Google Sheets...")
    append_to_sheet(jobs_df)
    print("Job fetching and uploading complete.")

if __name__ == "__main__":
    main()
