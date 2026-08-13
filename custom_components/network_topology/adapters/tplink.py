"""TP-Link router adapter backed by tplinkrouterc6u."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from urllib.parse import unquote

from .base import AdapterResult, ClientDevice, TopologyAdapter

CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

try:  # pragma: no cover - exercised in Home Assistant runtime.
    from tplinkrouterc6u import TPLinkRClient
except Exception:  # pragma: no cover - local tests monkeypatch this symbol.
    TPLinkRClient = None  # type: ignore[assignment]


class TPLinkAdapter(TopologyAdapter):
    """Fetch client/AP topology from a TP-Link local router session."""

    key = "tplink"
    label = "TP-Link Router"

    def __init__(
        self,
        *,
        hass,
        host: str,
        username: str,
        password: str,
    ) -> None:
        self._hass = hass
        self._host = host
        self._username = username
        self._password = password
        self._client = None

    @classmethod
    def config_schema(cls):
        """Return TP-Link connection fields for config flow."""

        import voluptuous as vol

        return vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

    async def fetch(self) -> AdapterResult:
        """Fetch and normalize one TP-Link topology snapshot."""

        return await self._hass.async_add_executor_job(self._fetch_sync)

    def _fetch_sync(self) -> AdapterResult:
        if TPLinkRClient is None:
            raise RuntimeError("tplinkrouterc6u is not installed")
        client = self._client or TPLinkRClient(self._host, self._username, self._password)
        try:
            client.authorize()
            result = self._read_client(client)
        except Exception:
            self._client = None
            client = TPLinkRClient(self._host, self._username, self._password)
            client.authorize()
            result = self._read_client(client)
        self._client = client
        return result

    def _read_client(self, client: Any) -> AdapterResult:
        firmware = _as_mapping(client.get_firmware())
        status = client.get_status()
        devices = [_map_device(device) for device in _status_devices(status)]
        return AdapterResult(
            devices=[device for device in devices if device.mac],
            root_label=str(firmware.get("model") or firmware.get("hardware_version") or self._host),
            root_ip=self._host,
        )


def _status_devices(status: Any) -> list[Any]:
    if isinstance(status, dict):
        return list(status.get("devices") or status.get("clients") or [])
    return list(getattr(status, "devices", None) or getattr(status, "clients", None) or [])


def _map_device(device: Any) -> ClientDevice:
    data = _as_mapping(device)
    hostname = str(_get(data, "hostname", default="") or "")
    return ClientDevice(
        mac=str(_get(data, "macaddr", "mac", default="") or ""),
        ip=_clean_optional(_get(data, "ipaddr", "ip")),
        hostname=unquote(hostname) or "unknown",
        ap_name=_clean_optional(_get(data, "ap_name")),
        ssid=_clean_optional(_get(data, "ssid")),
        frequency=_clean_optional(_get(data, "frequency", "freq_name")),
        signal=_clean_signal(_get(data, "signal", "rssi")),
        online=bool(_get(data, "active", "online", default=True)),
    )


def _as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, SimpleNamespace):
        return vars(value)
    return {
        key: getattr(value, key)
        for key in dir(value)
        if not key.startswith("_") and not callable(getattr(value, key))
    }


def _get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in data:
            return data[key]
    return default


def _clean_optional(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text == "---":
        return None
    return unquote(text)


def _clean_signal(value: Any) -> int | None:
    if value is None or value == "":
        return None
    text = str(value).replace("dBm", "").strip()
    try:
        return int(text)
    except ValueError:
        return None
