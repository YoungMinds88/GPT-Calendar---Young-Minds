from flask import Flask, request, jsonify
import datetime
import os.path
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'client_secret.json'

app = Flask(__name__)

def get_credentials():
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    else:
        # 1. Ve a esta URL manualmente desde tu navegador:
        auth_url = "PEGAR_AQUI_LA_URL_DE_AUTORIZACIÓN_GENERADA_EN_LOS_LOGS"
        print("👉 Abre este enlace en tu navegador para autorizar:")
        print(auth_url)

        # 2. Copia el 'code' que aparece en la URL después de dar permisos
        code = "PEGA_AQUI_EL_CODIGO_DE_AUTORIZACION_MANUALMENTE"

        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        flow.fetch_token(code=code)
        creds = flow.credentials

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds

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
