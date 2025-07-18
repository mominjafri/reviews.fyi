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
def add_review_to_sheet(rating, review_text):
    sheet = connect_to_sheet()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([timestamp, rating, review_text])



