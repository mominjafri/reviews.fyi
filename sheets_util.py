import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def connect_to_sheet():
    try:
        # Get credentials from environment
        creds_json = os.environ['GOOGLE_CREDENTIALS']
        creds_dict = json.loads(creds_json)
        
        # Fix private key formatting
        if '\\n' in creds_dict['private_key']:
            creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
        
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(credentials)
        
        # Try to open the sheet
        sheet = client.open("reviews-fyi").sheet1
        print("Successfully connected to Google Sheet")
        return sheet
        
    except Exception as e:
        print(f"Google Sheets connection failed: {str(e)}")
        raise

def add_review_to_sheet(first_name, last_name, email, company, linkedin,
                      rating, fairness, communication, technical, review):
    try:
        sheet = connect_to_sheet()
        row_data = [str(arg) if arg is not None else '' for arg in args]
        print(f"Attempting to append: {row_data}")
        sheet.append_row(row_data)
        print("Successfully saved to sheet")
        return True
    except Exception as e:
        print(f"Failed to save to sheet: {str(e)}")
        return False