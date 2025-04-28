import firebase_admin
from firebase_admin import credentials, db
import os
import json

# Cargar el JSON desde una variable de entorno
firebase_key = os.getenv("FIREBASE_KEY_JSON")

# Convertir el string a un objeto JSON
firebase_key_dict = json.loads(firebase_key)

# Usar ese objeto para inicializar las credenciales
cred = credentials.Certificate(firebase_key_dict)

firebase_url = os.getenv('FIREBASE_URL')

firebase_admin.initialize_app(cred, {
    'databaseURL': firebase_url
})

def get_server_loadouts(server_id):
    ref = db.reference(f'loadouts/{server_id}')
    return ref.get()

def save_server_loadouts(server_id, loadouts):
    ref = db.reference(f'loadouts/{server_id}')
    ref.set(loadouts)
