from google.oauth2 import service_account
from googleapiclient.discovery import build
from pymongo import MongoClient
import pandas as pd
from configs import *
from datetime import datetime, timedelta

def extract():
    # Load credentials
    SERVICE_ACCOUNT_FILE = 'creds.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Connect to API
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    # Sheet info
    SPREADSHEET_ID = spreadsheet_id  # Found in the URL of your sheet
    RANGE = spreadsheet_range  # Change as needed

    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[collection_name]

    now = datetime.now()
    week_ago = now - timedelta(weeks=1)
    week_ago = week_ago.strftime("%b-%Y")

    results = collection.find({"date": {"$regex": f"{week_ago}$"}}, projection={"_id": 0})
    df = pd.DataFrame.from_dict(results).to_dict(orient="split", index=False)

    # print(df)
    values = []
    # values.append(df['columns'])
    values.extend(df['data'])
    # # Data to write
    # values = [
    #     ['Name', 'Score'],
    #     ['Alice', 90],
    #     ['Bob', 85]
    # ]
    body = {'values': values}

    # Append rows to the sheet
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE,
        valueInputOption='RAW',  # or 'USER_ENTERED'
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

if __name__ == "__main__":
    extract()