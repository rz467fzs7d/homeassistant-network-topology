"""DataUpdateCoordinator for network topology adapters."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_ADAPTER, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .adapters import ADAPTERS


_LOGGER = logging.getLogger(__name__)


class NetworkTopologyCoordinator(DataUpdateCoordinator):
    """Poll one adapter and feed entities plus the panel store."""

    def __init__(self, hass, entry, store) -> None:
        self.entry = entry
        self.store = store
        self.adapter_key = entry.data[CONF_ADAPTER]
        adapter_cls = ADAPTERS[self.adapter_key]
        options = dict(entry.data)
        options.update(entry.options)
        self.adapter = adapter_cls(
            hass=hass,
            **{
                key: value
                for key, value in options.items()
                if key not in {CONF_ADAPTER, CONF_SCAN_INTERVAL}
            },
        )
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.adapter_key}",
            update_interval=timedelta(seconds=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
        )

    async def _async_update_data(self):
        """Fetch adapter data and update the store in one poll."""

        try:
            result = await self.adapter.fetch()
        except Exception as exc:
            self.store.set_error(exc)
            raise
        self.store.update_from_result(result, source=f"{self.adapter_key}-live")
        return result
