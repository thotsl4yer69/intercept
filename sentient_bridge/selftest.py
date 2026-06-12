"""No-infrastructure self-test: drive the simulator through the bridge with a
dry-run publisher and assert every active-spectrum topic is emitted with a
schema the GHOST fusion core accepts. No broker, no paho, no hardware."""

from __future__ import annotations

import sys

from . import schemas
from .bridge import SentientBridge
from .config import BridgeConfig
from .publisher import DryRunPublisher


def run_selftest(verbose: bool = True, raise_on_fail: bool = False) -> bool:
    pub = DryRunPublisher()
    bridge = SentientBridge(BridgeConfig(), pub)
    for _ in range(8):  # tick==4 inside this window emits the drone + corroboration
        bridge.run_once()

    seen = pub.topics_seen()
    checks = []

    def check(ok, label):
        checks.append((bool(ok), label))

    check(schemas.T_RF_CONTACT in seen, "emits rf/contact")
    check(schemas.T_BT_TRACKER in seen, "emits bt/tracker")
    check(schemas.T_TSCM_BASELINE in seen, "emits rf/tscm/baseline")
    check(schemas.T_DRONE in seen, "emits rf/drone/detection")

    # Schema spot-checks against what the fusion core reads.
    rf = [p for (t, p, _) in pub.messages if t == schemas.T_RF_CONTACT]
    check(all("id" in p and "classification" in p for p in rf), "rf/contact has id + classification")
    check(any(p["classification"] == "unknown" for p in rf), "at least one UNKNOWN emitter present")
    check(any(p["classification"] == "known" for p in rf), "known contacts present (context)")

    bt = [p for (t, p, _) in pub.messages if t == schemas.T_BT_TRACKER]
    rssis = [p["rssi"] for p in bt if "rssi" in p]
    check(len(rssis) >= 2 and rssis[-1] > rssis[0], "bt/tracker RSSI rises over time")

    tscm = [p for (t, p, _) in pub.messages if t == schemas.T_TSCM_BASELINE]
    check(all(isinstance(p.get("deltas"), list) for p in tscm), "tscm/baseline carries deltas[]")
    check(any(d.get("delta_db", 0) > 0 for p in tscm for d in p["deltas"]), "a positive baseline delta present")

    drone = [p for (t, p, _) in pub.messages if t == schemas.T_DRONE]
    check(all("classification" in p and "confidence" in p for p in drone), "drone has classification + confidence")

    ok_all = all(ok for ok, _ in checks)
    if verbose:
        print("iNTERCEPT sentient_bridge — dry-run self-test")
        for ok, label in checks:
            print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
        print(f"\n{sum(1 for ok, _ in checks if ok)}/{len(checks)} checks passed")
    if raise_on_fail and not ok_all:
        raise AssertionError("bridge self-test failures: "
                             + "; ".join(l for ok, l in checks if not ok))
    return ok_all


if __name__ == "__main__":
    sys.exit(0 if run_selftest(verbose=True) else 1)
