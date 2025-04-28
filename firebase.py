import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_server_loadouts(guild_id):
    return db.collection('servers').document(str(guild_id)).collection('loadouts')

