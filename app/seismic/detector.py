def detect_seismic_risk(event: dict):
    mag = float(event.get("magnitude", 0))
    depth = float(event.get("depth_km", 999))
    if mag >= 7.0 or (mag >= 6.0 and depth <= 20):
        return {"valid": True, "risk": "high"}
    if mag >= 5.0:
        return {"valid": True, "risk": "medium"}
    return {"valid": False, "risk": "low"}