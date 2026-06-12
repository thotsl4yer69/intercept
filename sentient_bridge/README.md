# sentient_bridge — iNTERCEPT → Sentient Core / GHOST

Additive bridge that publishes iNTERCEPT's **active-spectrum** detections onto
the `sentient/sensor/*` MQTT topics consumed by the
[GHOST Fusion Engine](https://github.com/thotsl4yer69/ghost-fusion). It is the
active half of the three-repo stack:

```
iNTERCEPT (this repo, active spectrum)  ─┐
                                         ├─►  ghost-fusion  ─► sentient/threat/*
RuView (WiFi-CSI, passive space)        ─┘
```

## Topics published (schemas match ghost-fusion exactly)

| Topic | From |
|---|---|
| `sentient/sensor/rf/contact` | RF/SDR emitter contacts (`classification`: `unknown`/`known`) |
| `sentient/sensor/rf/tscm/baseline` | TSCM baseline-sweep deltas (new energy vs clean sweep) |
| `sentient/sensor/rf/drone/detection` | drone classifier output |
| `sentient/sensor/bt/tracker` | Bluetooth/BLE tracker scans (rising RSSI ⇒ following) |

## Run

```bash
# No broker, no paho, no hardware — proves the schema contract:
python -m sentient_bridge --selftest        # expect 11/11 checks passed

# Watch the simulated stream as JSON (no broker):
python -m sentient_bridge --dry-run --ticks 10

# Publish to the live Sentient Core broker:
pip install -r sentient_bridge/requirements.txt
export SENTIENT_MQTT_HOST=192.168.1.159 SENTIENT_MQTT_USER=sentient SENTIENT_MQTT_PASS=...
python -m sentient_bridge
```

## Configuration (env, shared with the rest of the stack)

`SENTIENT_MQTT_HOST` (192.168.1.159) · `SENTIENT_MQTT_PORT` (1883) ·
`SENTIENT_MQTT_USER` (sentient) · `SENTIENT_MQTT_PASS` (unset — set it) ·
`INTERCEPT_BRIDGE_INTERVAL_SEC` (2.0) · `INTERCEPT_BRIDGE_SIM_SEED` (1312).

## Wiring real iNTERCEPT data

The bridge runs off a *source* with a `tick() -> list[(topic, payload)]` method;
the default is `ContactSimulator`. To publish live detections, implement a
source that maps iNTERCEPT internals onto the `schemas` builders — e.g.
`routes.bluetooth.detect_tracker`/`classify_bt_device` → `schemas.bt_tracker`,
the ADS-B / SDR classifier → `schemas.drone_detection` / `schemas.rf_contact` —
and pass it to `SentientBridge(cfg, publisher, source=...)`. The publish path is
unchanged.

---
Part of the GHOST / Sentient Core stack. Built on the upstream iNTERCEPT
platform (github.com/smittix/intercept, Apache-2.0); this module adds the MQTT
bridge only and changes none of the upstream code.
