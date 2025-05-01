from datetime import datetime, timedelta, timezone
from firebase_admin import firestore

db = firestore.client()

def set_premium(user_id: str, days: int = 30):
    """Otorga estado premium por X días."""
    premium_until = datetime.now(timezone.utc) + timedelta(days=days)
    premium_iso = premium_until.isoformat().replace("+00:00", "Z")

    db.collection("users").document(str(user_id)).set({
        "premium_until": premium_iso
    }, merge=True)

def is_premium(user_id: str) -> bool:
    """Verifica si un usuario es premium actualmente."""
    doc = db.collection("users").document(str(user_id)).get()
    if not doc.exists:
        return False

    data = doc.to_dict()
    premium_until = data.get("premium_until")
    if not premium_until:
        return False

    try:
        expiry = datetime.fromisoformat(premium_until.replace("Z", "+00:00"))
    except ValueError:
        return False

    return datetime.now(timezone.utc) < expiry

def get_premium_expiry(user_id: str) -> str:
    """Devuelve la fecha de expiración del premium (o None)."""
    doc = db.collection("users").document(str(user_id)).get()
    if not doc.exists:
        return None

    data = doc.to_dict()
    return data.get("premium_until")

def redeem_token(user_id: str, token: str, default_days: int = 30) -> bool:
    """Canjea un token y activa premium si es válido y no usado."""
    ref = db.collection("premium_tokens").document(token)
    doc = ref.get()

    if not doc.exists:
        return False

    data = doc.to_dict()
    if data.get("used_by"):
        return False

    # Usar duración personalizada si existe
    days = int(data.get("duration_days", default_days))

    # Marcar como usado
    ref.set({
        "used_by": user_id,
        "used_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }, merge=True)

    set_premium(user_id, days)
    return True

