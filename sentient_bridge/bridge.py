"""Ties a contact source (the simulator, or a real iNTERCEPT adapter) to a
publisher and drives it on an interval.

Real-source seam
----------------
To feed live data instead of the simulator, implement an object with a
``tick() -> list[(topic, payload)]`` method that maps iNTERCEPT detections onto
the ``schemas`` builders — e.g. wrap ``routes.bluetooth.detect_tracker`` for
``bt_tracker`` messages or the ADS-B / SDR classifier output for ``drone`` /
``rf_contact`` — and pass it as ``source``. The publishing path is identical.
"""

from __future__ import annotations

import logging
import time

from .config import BridgeConfig
from .simulator import ContactSimulator

log = logging.getLogger("sentient_bridge.bridge")


class SentientBridge:
    def __init__(self, config: BridgeConfig, publisher, source=None):
        self.cfg = config
        self.publisher = publisher
        self.source = source or ContactSimulator(seed=config.sim_seed)

    def run_once(self) -> int:
        """Pull one round from the source and publish it. Returns msg count."""
        messages = self.source.tick()
        for topic, payload in messages:
            self.publisher.publish(topic, payload, retain=False)
        return len(messages)

    def run(self, max_ticks: int | None = None, sleep: bool = True) -> None:
        self.publisher.connect()
        try:
            n = 0
            while max_ticks is None or n < max_ticks:
                count = self.run_once()
                log.debug("published round", extra={"extra": {"tick": n, "messages": count}})
                n += 1
                if sleep:
                    time.sleep(self.cfg.publish_interval_sec)
        finally:
            self.publisher.close()
