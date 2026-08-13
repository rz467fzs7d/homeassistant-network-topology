"""Device tracker entities for network topology clients."""

from __future__ import annotations

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType
from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, format_mac
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .utils import signal_level


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up tracked client entities for the config entry."""

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    known_macs: set[str] = set()

    def add_new_entities() -> None:
        entities = []
        for device in (coordinator.data.devices if coordinator.data else []):
            if not device.mac:
                continue
            mac = format_mac(device.mac)
            if mac in known_macs:
                continue
            known_macs.add(mac)
            entities.append(NetworkClientTracker(coordinator, device))
        if entities:
            async_add_entities(entities)

    add_new_entities()
    entry.async_on_unload(coordinator.async_add_listener(add_new_entities))


class NetworkClientTracker(CoordinatorEntity, TrackerEntity):
    """Represent one network client as a router device tracker."""

    _attr_entity_registry_enabled_default = True
    _attr_should_poll = False
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, device) -> None:
        super().__init__(coordinator)
        self._mac = device.mac
        self._attr_unique_id = format_mac(device.mac)
        self._attr_name = f"nt_{device.hostname}"

    @property
    def source_type(self):
        return SourceType.ROUTER

    @property
    def is_connected(self) -> bool:
        device = self._device
        return bool(device and device.online)

    @property
    def ip_address(self) -> str | None:
        return self._device.ip if self._device else None

    @property
    def mac_address(self) -> str:
        return self._mac

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        device = self._device
        if device is None:
            return {}
        return {
            "ap_name": device.ap_name,
            "ssid": device.ssid,
            "frequency": device.frequency,
            "ip": device.ip,
            "signal_level": signal_level(device.signal),
        }

    @property
    def device_info(self):
        return {
            "connections": {(CONNECTION_NETWORK_MAC, format_mac(self._mac))},
            "identifiers": {(DOMAIN, format_mac(self._mac))},
            "name": self._device.hostname if self._device else self._mac,
        }

    @property
    def _device(self):
        if not self.coordinator.data:
            return None
        normalized = format_mac(self._mac)
        for device in self.coordinator.data.devices:
            if format_mac(device.mac) == normalized:
                return device
        return None
