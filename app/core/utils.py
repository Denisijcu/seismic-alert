import json
import re


def strip_json_fences(raw: str) -> str:
    """Quita los ```json ... ``` fences que algunos LLMs agregan."""
    if not raw:
        return raw
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def extract_severity(classification_raw: str) -> str:
    """Extrae el campo 'severity' del JSON crudo del classifier."""
    try:
        data = json.loads(strip_json_fences(classification_raw))
        return data.get("severity", "unknown")
    except Exception:
        return "unknown"


def clean_message(message: str) -> str:
    """Quita comillas envolventes que el LLM a veces agrega por error."""
    if not message:
        return message
    cleaned = message.strip()
    if len(cleaned) >= 2 and cleaned[0] == '"' and cleaned[-1] == '"':
        cleaned = cleaned[1:-1]
    return cleaned