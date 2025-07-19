import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def connect_to_sheet():
    # Get and parse credentials
    creds_json = os.environ['GOOGLE_CREDENTIALS']
    creds_dict = json.loads(creds_json)
    
    # Ensure proper key formatting
    if '\\n' in creds_dict['private_key']:
        creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
    
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(credentials).open("reviews-fyi").sheet1

def add_review_to_sheet(*args):
    try:
        sheet = connect_to_sheet()
        sheet.append_row([str(arg) if arg is not None else '' for arg in args])
        return True
    except Exception as e:
        print(f"Sheets Error: {str(e)}")
        return False