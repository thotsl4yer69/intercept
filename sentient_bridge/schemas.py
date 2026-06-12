"""Payload + topic builders for the active-spectrum layer.

These match the schemas documented in ghost-fusion's README exactly. Keeping
them in one place means the iNTERCEPT bridge and the fusion engine can never
drift. Every builder fills only the fields the fusion core reads; publishers may
add extra keys freely (the core ignores unknowns and applies safe defaults).
"""

from __future__ import annotations

# Topics (active-spectrum layer).
T_RF_CONTACT = "sentient/sensor/rf/contact"
T_TSCM_BASELINE = "sentient/sensor/rf/tscm/baseline"
T_DRONE = "sentient/sensor/rf/drone/detection"
T_BT_TRACKER = "sentient/sensor/bt/tracker"


def rf_contact(
    contact_id: str,
    classification: str = "unknown",
    band: str | None = None,
    rssi: float | None = None,
    **extra,
) -> dict:
    """sentient/sensor/rf/contact — one emitter per message.

    ``classification`` is "unknown" or "known"; only "unknown" can ever drive a
    PLANTED_DEVICE conclusion downstream.
    """
    payload = {"id": contact_id, "classification": classification}
    if band is not None:
        payload["band"] = band
    if rssi is not None:
        payload["rssi"] = rssi
    payload.update(extra)
    return payload


def tscm_baseline(deltas: list) -> dict:
    """sentient/sensor/rf/tscm/baseline — batch of baseline-sweep deltas.

    Each delta with ``delta_db > 0`` is new energy versus the clean sweep and is
    treated as an unknown emitter by the fusion core.
    """
    return {"deltas": list(deltas)}


def baseline_delta(
    delta_id: str,
    band: str | None = None,
    delta_db: float = 0.0,
    rssi: float | None = None,
    classification: str = "unknown",
) -> dict:
    d = {"id": delta_id, "delta_db": delta_db, "classification": classification}
    if band is not None:
        d["band"] = band
    if rssi is not None:
        d["rssi"] = rssi
    return d


def drone_detection(
    classification: str,
    confidence: float,
    band: str | None = None,
    detection_id: str | None = None,
    **extra,
) -> dict:
    """sentient/sensor/rf/drone/detection — DeepSig/MobileNetV2-style output."""
    payload = {"classification": classification, "confidence": confidence}
    if band is not None:
        payload["band"] = band
    if detection_id is not None:
        payload["id"] = detection_id
    payload.update(extra)
    return payload


def bt_tracker(
    tracker_id: str,
    rssi: float | None = None,
    name: str | None = None,
    **extra,
) -> dict:
    """sentient/sensor/bt/tracker — BT/BLE scan; rising RSSI => following."""
    payload = {"id": tracker_id}
    if rssi is not None:
        payload["rssi"] = rssi
    if name is not None:
        payload["name"] = name
    payload.update(extra)
    return payload
