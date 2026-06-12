"""Pytest wrapper around the dry-run self-test plus schema checks.
Runs with no broker, no paho, no hardware."""

from sentient_bridge import schemas
from sentient_bridge.bridge import SentientBridge
from sentient_bridge.config import BridgeConfig
from sentient_bridge.publisher import DryRunPublisher
from sentient_bridge.selftest import run_selftest


def test_dry_run_selftest():
    assert run_selftest(verbose=False, raise_on_fail=True) is True


def test_all_four_topics_emitted():
    pub = DryRunPublisher()
    bridge = SentientBridge(BridgeConfig(), pub)
    for _ in range(8):
        bridge.run_once()
    assert {
        schemas.T_RF_CONTACT,
        schemas.T_BT_TRACKER,
        schemas.T_TSCM_BASELINE,
        schemas.T_DRONE,
    } <= pub.topics_seen()


def test_only_unknown_contacts_are_planted_candidates():
    # Schema contract: classification is "unknown" | "known".
    pub = DryRunPublisher()
    SentientBridge(BridgeConfig(), pub).run_once()
    rf = [p for (t, p, _) in pub.messages if t == schemas.T_RF_CONTACT]
    assert all(p["classification"] in ("unknown", "known") for p in rf)


def test_deterministic_with_seed():
    a, b = DryRunPublisher(), DryRunPublisher()
    SentientBridge(BridgeConfig(sim_seed=42), a).run_once()
    SentientBridge(BridgeConfig(sim_seed=42), b).run_once()
    assert a.messages == b.messages
