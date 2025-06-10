import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Charge un fichier JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")

def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
    """Sauvegarde un dictionnaire en JSON"""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {e}")
        return False

def generate_hash(text: str) -> str:
    """Génère un hash MD5 d'un texte"""
    return hashlib.md5(text.encode()).hexdigest()

def format_duration(seconds: int) -> str:
    """Formate une durée en secondes en format lisible"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}m {seconds}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def is_business_hours(start_hour: int = 9, end_hour: int = 18) -> bool:
    """Vérifie si nous sommes dans les heures d'ouverture"""
    now = datetime.now()
    return start_hour <= now.hour < end_hour and now.weekday() < 5
