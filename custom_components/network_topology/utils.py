"""Pure helpers shared by Network Topology platforms."""

from __future__ import annotations


def signal_level(signal: int | None) -> str | None:
    """Return a recorder-friendly signal band."""

    if signal is None:
        return None
    if signal > -60:
        return "strong"
    if signal < -75:
        return "weak"
    return "medium"
