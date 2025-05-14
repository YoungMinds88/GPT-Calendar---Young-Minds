from flask import Flask, request, jsonify
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
import os

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'

def get_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    return creds

@app.route('/crear-evento', methods=['POST'])
def crear_evento():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    else:
        creds = get_credentials()

    service = build('calendar', 'v3', credentials=creds)
    data = request.get_json()

    event = {
        'summary': data.get('title'),
        'location': data.get('location'),
        'start': {
            'dateTime': data.get('start_time'),
            'timeZone': 'Europe/Madrid',
        },
        'end': {
            'dateTime': data.get('end_time'),
            'timeZone': 'Europe/Madrid',
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    return jsonify({'status': 'ok', 'event_link': event.get('htmlLink')})

if __name__ == '__main__':
    app.run(debug=True)
