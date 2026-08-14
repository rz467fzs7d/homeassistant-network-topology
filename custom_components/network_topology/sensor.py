"""Diagnostic sensor entities for network topology sources."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .adapters import ADAPTERS
from .const import CONF_ADAPTER, CONF_HOST, DOMAIN


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up the topology source entity for a config entry."""

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([NetworkTopologySourceSensor(coordinator, entry)])


class NetworkTopologySourceSensor(CoordinatorEntity, SensorEntity):
    """Represent one configured network topology source."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._adapter = ADAPTERS[entry.data[CONF_ADAPTER]]
        self._attr_unique_id = f"{entry.entry_id}_topology_source"
        self._attr_name = entry.title

    @property
    def icon(self) -> str:
        """Return the adapter-specific icon for this source instance."""

        return self._adapter.icon

    @property
    def native_value(self) -> str:
        """Return a simple source health state."""

        return "online" if self.coordinator.last_update_success else "error"

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Expose source metadata for diagnostics."""

        data = self.coordinator.data
        return {
            "brand": self._adapter.brand,
            "model": self._adapter.model,
            "adapter": self._adapter.key,
            "host": self._entry.data.get(CONF_HOST),
            "device_count": len(data.devices) if data else 0,
            "root_label": data.root_label if data else None,
            "root_ip": data.root_ip if data else None,
        }

    @property
    def device_info(self):
        """Return device registry metadata for the configured source."""

        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.title,
            "manufacturer": self._adapter.brand,
            "model": self._adapter.model,
        }
