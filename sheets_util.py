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

def add_review_to_sheet(*args):
    try:
        sheet = connect_to_sheet()
        sheet.append_row(list(args))
        return True
    except Exception as e:
        print(f"Error writing to sheet: {str(e)}")
        return False