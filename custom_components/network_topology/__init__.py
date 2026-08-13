"""Read-only network topology integration."""

from __future__ import annotations

from typing import Any
from pathlib import Path

from homeassistant.components.http import HomeAssistantView
from homeassistant.components import frontend
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import API_PATH, DOMAIN, FRONTEND_URL, PANEL_NAME, PANEL_TITLE, PANEL_URL_PATH, PLATFORMS
from .store import TopologyStore
from .coordinator import NetworkTopologyCoordinator


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the network topology HTTP API."""

    domain_data = hass.data.setdefault(DOMAIN, {})
    domain_data.setdefault("store", TopologyStore())
    _register_frontend(hass)
    _register_view(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up live topology polling from a config entry."""

    domain_data = hass.data.setdefault(DOMAIN, {})
    store = domain_data.setdefault("store", TopologyStore())
    coordinator = NetworkTopologyCoordinator(hass, entry, store)
    domain_data[entry.entry_id] = {"coordinator": coordinator}
    _register_frontend(hass)
    _register_view(hass)
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a network topology config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


def _register_view(hass: HomeAssistant) -> None:
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get("view_registered"):
        return
    hass.http.register_view(NetworkTopologyView(hass))
    domain_data["view_registered"] = True


def _register_frontend(hass: HomeAssistant) -> None:
    """Register bundled frontend assets and sidebar panel once."""

    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get("frontend_registered"):
        return
    frontend_path = Path(__file__).parent / "frontend"
    hass.http.register_static_path(FRONTEND_URL, str(frontend_path), cache_headers=True)
    frontend.async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title=PANEL_TITLE,
        sidebar_icon="mdi:access-point-network",
        frontend_url_path=PANEL_URL_PATH,
        config={
            "_panel_custom": {
                "name": PANEL_NAME,
                "module_url": f"{FRONTEND_URL}/network-topology-panel.js",
                "embed_iframe": False,
            }
        },
        require_admin=False,
    )
    domain_data["frontend_registered"] = True


class NetworkTopologyView(HomeAssistantView):
    """Expose topology data to the frontend panel."""

    url = API_PATH
    name = "api:network_topology:topology"
    requires_auth = True

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass

    async def get(self, request: Any) -> Any:
        store = self._hass.data[DOMAIN]["store"]
        return self.json(store.snapshot())
