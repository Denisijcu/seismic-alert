import httpx
from app.core.config import settings


def _send_telegram(message: str) -> dict:
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return {"ok": False, "error": "Telegram no configurado (falta token o chat_id)"}

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        return {"ok": True, "response": response.json()}
    except httpx.HTTPError as e:
        return {"ok": False, "error": str(e)}


def dispatch_alert(message: str, channels: list[str]) -> dict:
    results = {}

    if "telegram" in channels:
        results["telegram"] = _send_telegram(message)

    # push y sms quedan mockeados por ahora
    if "push" in channels:
        results["push"] = {"ok": True, "mocked": True}
    if "sms" in channels:
        results["sms"] = {"ok": True, "mocked": True}

    sent = all(r.get("ok", False) for r in results.values()) if results else False

    return {
        "sent": sent,
        "channels": channels,
        "message": message,
        "results": results,
    }