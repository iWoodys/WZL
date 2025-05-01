import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import tempfile

# Obtener clave Firebase desde variable de entorno
firebase_key_json = os.getenv("FIREBASE_KEY_JSON")

if firebase_key_json is None:
    raise ValueError("FIREBASE_KEY_JSON no está definida en las variables de entorno.")

# Decodificar correctamente los caracteres escapados (\n)
firebase_key_json_decoded = bytes(firebase_key_json, "utf-8").decode("unicode_escape")
firebase_dict = json.loads(firebase_key_json_decoded)

# Guardar en archivo temporal
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
    json.dump(firebase_dict, temp_file)
    temp_file_path = temp_file.name

# Inicializar Firebase
cred = credentials.Certificate(temp_file_path)
firebase_admin.initialize_app(cred)

db = firestore.client()

# Funciones
def get_server_loadouts(server_id):
    return db.collection('loadouts').document(str(server_id)).collection('items')

def save_server_loadout(server_id, weapon_name, data):
    ref = db.collection('loadouts').document(str(server_id)).collection('items').document(weapon_name)
    ref.set(data)

def delete_server_loadout(server_id, weapon_name):
    ref = db.collection('loadouts').document(str(server_id)).collection('items').document(weapon_name)
    ref.delete()

def get_single_loadout(server_id, weapon_name):
    ref = db.collection('loadouts').document(str(server_id)).collection('items').document(weapon_name)
    return ref.get()

