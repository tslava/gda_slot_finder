from datetime import datetime
from typing import Dict
from typing import List

import gspread
from google.oauth2 import service_account
from gspread import WorksheetNotFound

from settings import GOOGLE_CREDENTIALS_FILE_PATH


def write_to_google_sheet(data: List[Dict], table_doc_id: str) -> None:
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE_PATH)
    scoped_credentials = credentials.with_scopes(scope)
    client = gspread.authorize(scoped_credentials)

    try:
        spreadsheet = client.open_by_key(table_doc_id)
    except gspread.exceptions.APIError:
        print("gspread.exceptions.APIError - return None")
        return None

    # Create headers from the keys of the first dictionary
    headers = list(data[0].keys())

    # Prepare the data to be written
    rows = []
    for item in data:
        row = []
        for key in headers:
            if key in item:
                value = item[key]
                if isinstance(value, datetime):
                    # value = value.strftime('%Y-%m-%dT%H:%M:%S%z')
                    value = value.strftime('%H:%M:%S%z')
                if isinstance(value, list):
                    value = ' '.join(value)
                row.append(value)
            else:
                row.append('')
        rows.append(row)

    sheet_name = datetime.now().strftime('%Y-%m-%d')
    try:
        sheet = spreadsheet.worksheet(sheet_name)
    except WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(sheet_name, cols=15, rows=10000)
        sheet.append_row(headers)

    sheet.append_rows(rows)
