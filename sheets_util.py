import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def connect_to_sheet():
    """
    Connect to Google Sheet with comprehensive error handling
    Returns: gspread Worksheet object
    Raises: Exception with detailed error message
    """
    try:
        # 1. Load credentials from environment
        creds_json = os.environ.get('GOOGLE_CREDENTIALS')
        if not creds_json:
            raise ValueError("GOOGLE_CREDENTIALS environment variable not set")
        
        # 2. Parse and validate credentials
        creds_dict = json.loads(creds_json)
        required_keys = ['type', 'project_id', 'private_key', 'client_email']
        if not all(key in creds_dict for key in required_keys):
            raise ValueError("Invalid Google credentials format")
        
        # 3. Fix private key formatting
        if '\\n' in creds_dict['private_key']:
            creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
        
        # 4. Set authentication scopes
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # 5. Authenticate
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
        client = gspread.authorize(credentials)
        
        # 6. Open specific sheet
        sheet_name = os.environ.get('GOOGLE_SHEET_NAME', 'reviews-fyi')
        return client.open(sheet_name).sheet1
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in credentials: {str(e)}")
    except Exception as e:
        raise Exception(f"Google Sheets connection failed: {repr(e)}")

def add_review_to_sheet(first_name, last_name, email, company, role, years_experience, linkedin,
                       rating, fairness, communication, technical, leadership, review):
    """
    Append review data to Google Sheet
    Returns: bool (True if successful)
    """
    try:
        sheet = connect_to_sheet()
        sheet.append_row([
            first_name,
            last_name,
            email,
            company,
            role,
            years_experience,
            linkedin if linkedin else '',  # Handle empty LinkedIn
            rating,
            fairness,
            communication,
            technical,
            leadership,
            review
        ])
        return True
    except Exception as e:
        print(f"Failed to save review: {repr(e)}")
        return False