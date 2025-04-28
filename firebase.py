import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Cargar las credenciales desde variable de entorno
firebase_key = os.getenv("FIREBASE_KEY_JSON")
firebase_key_dict = json.loads(firebase_key)
firebase_key_dict["private_key"] = firebase_key_dict["private_key"].replace("\\n", "\n")

# Inicializar la app de Firebase
cred = credentials.Certificate(firebase_key_dict)
firebase_admin.initialize_app(cred)

# Crear cliente de Firestore
db = firestore.client()

def get_server_loadouts(server_id):
    """Devuelve la colección de loadouts para un servidor."""
    return db.collection('loadouts').document(str(server_id)).collection('items')

def save_server_loadout(server_id, weapon_name, data):
    """Guarda o actualiza un loadout específico."""
    ref = db.collection('loadouts').document(str(server_id)).collection('items').document(weapon_name)
    ref.set(data)

def delete_server_loadout(server_id, weapon_name):
    """Elimina un loadout específico."""
    ref = db.collection('loadouts').document(str(server_id)).collection('items').document(weapon_name)
    ref.delete()

def get_single_loadout(server_id, weapon_name):
    """Obtiene un solo loadout específico."""
    ref = db.collection('loadouts').document(str(server_id)).collection('items').document(weapon_name)
    return ref.get()

