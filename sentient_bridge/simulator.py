"""Hardware-free contact simulator.

Produces a deterministic, evolving stream across all four active-spectrum topics
so the bridge can be exercised end-to-end with no SDR, no Bluetooth radio and no
broker. Mirrors the kinds of contacts iNTERCEPT surfaces in the field:

* a steady **known** Wi-Fi AP,
* a lingering **unknown** emitter (the candidate "planted device" the fusion
  engine escalates only if RuView later confirms the room empty),
* a **BT tracker** whose RSSI rises tick over tick (a following tracker),
* periodic **TSCM baseline** deltas (new energy vs the clean sweep),
* an occasional **drone** classifier hit with corroborating RF in band.
"""

from __future__ import annotations

import random

from . import schemas


class ContactSimulator:
    def __init__(self, seed: int = 1312):
        self._rng = random.Random(seed)
        self._tick = 0
        self._tracker_rssi = -92.0

    def _jitter(self, base: float, spread: float) -> float:
        return round(base + self._rng.uniform(-spread, spread), 1)

    def tick(self) -> list[tuple[str, dict]]:
        """Return this round's (topic, payload) messages and advance state."""
        out: list[tuple[str, dict]] = []
        t = self._tick

        # Steady KNOWN Wi-Fi AP — world-state context, never scored as a threat.
        out.append((schemas.T_RF_CONTACT, schemas.rf_contact(
            "ap:home-router", classification="known", band="2.4GHz",
            rssi=self._jitter(-45, 2))))

        # Lingering UNKNOWN emitter — dwell grows each tick.
        out.append((schemas.T_RF_CONTACT, schemas.rf_contact(
            "unk:433-pulse", classification="unknown", band="433MHz",
            rssi=self._jitter(-67, 3))))

        # BT tracker with rising RSSI (a following tracker).
        self._tracker_rssi = min(-55.0, self._tracker_rssi + 3.0)
        out.append((schemas.T_BT_TRACKER, schemas.bt_tracker(
            "bt:AA-BB-CC-DD-EE-FF", rssi=self._tracker_rssi, name="Tag")))

        # Periodic TSCM baseline sweep — surface new energy above baseline.
        if t % 3 == 0:
            out.append((schemas.T_TSCM_BASELINE, schemas.tscm_baseline([
                schemas.baseline_delta("sweep:1.2GHz", band="1.2GHz",
                                       delta_db=self._jitter(7, 1),
                                       rssi=self._jitter(-70, 2)),
            ])))

        # Occasional drone hit + corroborating RF in the same band.
        if t == 4:
            out.append((schemas.T_RF_CONTACT, schemas.rf_contact(
                "rf:5g8-video", classification="known", band="5.8GHz",
                rssi=self._jitter(-58, 2))))
            out.append((schemas.T_DRONE, schemas.drone_detection(
                classification="drone", confidence=0.93, band="5.8GHz",
                detection_id="drn:1")))

        self._tick += 1
        return out
