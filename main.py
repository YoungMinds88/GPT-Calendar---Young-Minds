
from flask import Flask, request, jsonify, redirect
from werkzeug.middleware.proxy_fix import ProxyFix
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
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

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

@app.route("/cancel-evento", methods=["POST"])
def cancel_event():
    data = request.get_json()
    event_id = data.get("event_id")
    
    if not event_id:
        return jsonify({"error": "Falta el ID del evento"}), 400

    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    try:
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return jsonify({"status": "Evento cancelado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from flask import send_file  # Asegúrate de que esta línea esté al principio del archivo

@app.route("/openapi.yaml")
def serve_openapi():
    return send_file("openapi.yaml", mimetype="text/yaml")

from flask import send_from_directory

@app.route('/.well-known/ai-plugin.json')
def serve_ai_plugin():
    return send_from_directory('.well-known', 'ai-plugin.json', mimetype='application/json')

@app.route('/openapi.yaml')
def serve_openapi():
    return send_from_directory('.', 'openapi.yaml', mimetype='text/yaml')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
