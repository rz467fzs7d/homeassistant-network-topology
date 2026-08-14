"""Brand-neutral network topology adapter contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ClientDevice:
    """One client device as seen by a network controller."""

    mac: str
    ip: str | None
    hostname: str
    ap_name: str | None = None
    ssid: str | None = None
    frequency: str | None = None
    signal: int | None = None
    online: bool = True


@dataclass(frozen=True)
class AdapterResult:
    """One topology poll result shared by entities and the panel API."""

    devices: list[ClientDevice]
    root_label: str
    root_ip: str


class TopologyAdapter(ABC):
    """Base class for vendor-specific topology adapters."""

    key: str
    label: str
    brand: str = "Network"
    model: str = "Topology Controller"
    icon: str = "mdi:access-point-network"

    @classmethod
    @abstractmethod
    def config_schema(cls):
        """Return this adapter's config-flow schema."""

    @abstractmethod
    async def fetch(self) -> AdapterResult:
        """Fetch one normalized topology snapshot."""
