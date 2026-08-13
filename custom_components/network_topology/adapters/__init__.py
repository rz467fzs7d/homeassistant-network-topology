"""Adapter registry for network_topology."""

from __future__ import annotations

from .tplink import TPLinkAdapter


ADAPTERS = {
    TPLinkAdapter.key: TPLinkAdapter,
}
