import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_google_credentials():
    """Load credentials from environment variable"""
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if not creds_json:
        raise ValueError("Google credentials not found in environment variables")
    return json.loads(creds_json)

def connect_to_sheet():
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        get_google_credentials(), scope)
    client = gspread.authorize(credentials)
    return client.open("reviews-fyi").sheet1
    
def add_review_to_sheet(first_name, last_name, email, company, linkedin, 
                       rating, fairness, communication, technical, review):
    try:
        sheet = connect_to_sheet()
        # Convert empty string to None if needed
        linkedin = linkedin if linkedin else None
        sheet.append_row([
            first_name, last_name, email, company, linkedin,
            rating, fairness, communication, technical, review
        ])
        return True
    except Exception as e:
        print(f"Google Sheets Error: {str(e)}")
        return False