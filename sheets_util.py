import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from datetime import datetime

# Connect to Google Sheets
def connect_to_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    # Open by sheet name or URL
    sheet = client.open("reviews-fyi").sheet1  # Replace with your actual Sheet name
    return sheet

# Add a row to the sheet
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def connect_to_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("reviews-fyi").sheet1  # Make sure your spreadsheet has the correct columns in this order
    return sheet

def add_review_to_sheet(boss_first, boss_last, boss_email, company, linkedin_url, overall_rating, fairness, communication, technical, review_text):
    sheet = connect_to_sheet()
    row = [
        boss_first.strip(),
        boss_last.strip(),
        boss_email.strip(),
        company.strip(),
        linkedin_url.strip() if linkedin_url else "",
        overall_rating.strip(),
        fairness.strip(),
        communication.strip(),
        technical.strip(),
        review_text.strip()
    ]
    sheet.append_row(row)



