"""Runtime cache for network topology snapshots."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from .topology import build_topology


class TopologyStore:
    """Expose the coordinator's latest data as a panel snapshot."""

    def __init__(self, *, source: str = "network-topology") -> None:
        self._topology: dict[str, Any] = build_topology(
            devices=[],
            root_label="Network",
            root_ip="",
            source=source,
        )
        self._refresh_count = 0
        self._last_success_at: str | None = None
        self._last_error: str | None = "Network topology is not configured"

    def update_from_result(self, result: Any, *, source: str) -> None:
        """Replace the snapshot with a successful adapter result."""

        self._topology = build_topology(
            devices=result.devices,
            root_label=result.root_label,
            root_ip=result.root_ip,
            source=source,
        )
        self._refresh_count += 1
        self._last_success_at = datetime.now(timezone.utc).isoformat()
        self._last_error = None

    def set_error(self, error: Exception | str) -> None:
        """Keep the last good snapshot while exposing refresh failure."""

        if isinstance(error, Exception):
            self._last_error = f"{type(error).__name__}: {error}"
            return
        self._last_error = str(error)

    def snapshot(self) -> dict[str, Any]:
        """Return a copy of the latest topology plus refresh state."""

        topology = deepcopy(self._topology)
        topology["refresh"] = {
            "ok": self._last_error is None,
            "last_success_at": self._last_success_at,
            "last_error": self._last_error,
            "refresh_count": self._refresh_count,
        }
        return topology
