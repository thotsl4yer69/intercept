"""sentient_bridge — publish iNTERCEPT signal-intelligence contacts onto the
GHOST / Sentient Core MQTT spine.

This is an additive module on top of the upstream iNTERCEPT platform
(github.com/smittix/intercept, Apache-2.0). It maps iNTERCEPT's active-spectrum
detections — RF/SDR contacts, TSCM baseline deltas, drone classifier hits and
Bluetooth trackers — onto the ``sentient/sensor/*`` topics consumed by the
GHOST Fusion Engine, using the exact schemas defined in ghost-fusion's README.

It is deliberately import-light: the simulator and the dry-run publisher need
neither ``paho-mqtt`` nor any SDR hardware, so the bridge is fully testable in
CI. ``paho-mqtt`` is imported lazily only when actually publishing to a broker.
"""

__version__ = "0.1.0"
