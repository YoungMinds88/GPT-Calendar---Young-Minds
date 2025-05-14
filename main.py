
from flask import Flask, request, jsonify, redirect
import datetime
import os.path
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'client_secret.json'

app = Flask(__name__)

flow = Flow.from_client_secrets_file(
    CREDENTIALS_FILE,
    scopes=SCOPES,
    redirect_uri='https://gpt-calendar-young-minds.onrender.com/oauth2callback'
)

@app.route("/authorize")
def authorize():
    auth_url, _ = flow.authorization_url(prompt='consent')
    return jsonify({"auth_url": auth_url})

@app.route("/oauth2callback")
def oauth2callback():
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    return "✅ Autorización completada. Ya puedes cerrar esta pestaña."

def get_credentials():
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        return creds
    else:
        raise Exception("❌ Aún no se ha autorizado el acceso. Ve a /authorize para obtener el enlace.")

@app.route("/crear-evento", methods=["POST"])
def crear_evento():
    try:
        data = request.get_json()
        titulo = data.get("title")
        inicio = data.get("start_time")
        fin = data.get("end_time")
        ubicacion = data.get("location", "")

        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)

        evento = {
            'summary': titulo,
            'location': ubicacion,
            'start': {
                'dateTime': inicio,
                'timeZone': 'Europe/Madrid',
            },
            'end': {
                'dateTime': fin,
                'timeZone': 'Europe/Madrid',
            },
        }

        event = service.events().insert(calendarId='primary', body=evento).execute()
        return jsonify({"status": "success", "event_id": event['id']})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
