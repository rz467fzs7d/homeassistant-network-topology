"""TP-Link AC/router adapter backed by the local web API."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import unquote

import aiohttp

from .base import AdapterResult, ClientDevice, TopologyAdapter

CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

_LOGGER = logging.getLogger(__name__)

AUTH_KEY = "RDpbLfCPsJZ7fiv"
AUTH_DICT = (
    "yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW"
)


class TPLinkAdapter(TopologyAdapter):
    """Fetch client/AP topology from a TP-Link local router session."""

    key = "tplink"
    label = "TP-Link TL-R489GP-AC"

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
        self._stok: str | None = None
        self._timeout = aiohttp.ClientTimeout(total=10)

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

        host_rows = await self._query_table("host_management", "host_info")
        static_rows = await self._query_table("dhcpd", "dhcp_static")
        devices = [_map_device(row, static_rows) for row in host_rows]
        _LOGGER.debug(
            "Fetched TP-Link web topology host=%s raw_devices=%s mapped_devices=%s",
            self._host,
            len(host_rows),
            len([device for device in devices if device.mac]),
        )
        return AdapterResult(
            devices=[device for device in devices if device.mac],
            root_label="TL-R489GP-AC",
            root_ip=self._host,
        )

    async def _query_table(self, module: str, table: str) -> list[dict[str, Any]]:
        result = await self._api({"method": "get", module: {"table": table}})
        if result.get("error_code") != 0:
            raise RuntimeError(f"TP-Link API error {result.get('error_code')}")
        return _flatten_table(result.get(module, {}), table)

    async def _api(self, payload: dict[str, Any]) -> dict[str, Any]:
        await self._ensure_login()
        try:
            return await self._post_api(payload)
        except aiohttp.ClientResponseError as exc:
            if exc.status not in {401, 403}:
                raise
        self._stok = None
        await self._ensure_login()
        return await self._post_api(payload)

    async def _post_api(self, payload: dict[str, Any]) -> dict[str, Any]:
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            async with session.post(
                f"http://{self._host}/stok={self._stok}/ds",
                json=payload,
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def _ensure_login(self) -> None:
        if self._stok:
            return
        payload = {
            "method": "do",
            "login": {
                "username": self._username,
                "password": _security_encode(self._password),
            },
        }
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            async with session.post(f"http://{self._host}", json=payload) as response:
                response.raise_for_status()
                body = await response.json()
        if body.get("error_code") != 0 or not body.get("stok"):
            raise RuntimeError(f"TP-Link login failed: error_code={body.get('error_code')}")
        self._stok = str(body["stok"])


def _map_device(row: dict[str, Any], static_rows: list[dict[str, Any]]) -> ClientDevice:
    hostname = str(_get(row, "hostname", "name", default="") or "")
    mac = str(_get(row, "mac", "macaddr", default="") or "")
    ip = _clean_optional(_get(row, "ip", "ipaddr"))
    return ClientDevice(
        mac=mac,
        ip=ip,
        hostname=unquote(hostname) or "unknown",
        ap_name=_clean_optional(_get(row, "ap_name", "apName", "wireless_ap_name")),
        ssid=_clean_optional(_get(row, "ssid", "ssid_name")),
        frequency=_clean_optional(_get(row, "wire_type", "frequency", "freq_name")),
        signal=_clean_signal(_get(row, "signal", "rssi")),
        online=bool(_get(row, "active", "online", default=True)),
    )


def _flatten_table(section: dict[str, Any], table_name: str) -> list[dict[str, Any]]:
    rows = section.get(table_name, [])
    if not isinstance(rows, list):
        return []
    flattened: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict) or len(row) != 1:
            continue
        row_id, value = next(iter(row.items()))
        if not isinstance(value, dict):
            continue
        item = {
            key: _clean_value(value)
            for key, value in value.items()
            if not key.startswith(".")
        }
        item.setdefault("_row", row_id)
        flattened.append(item)
    return flattened


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


def _clean_value(value: Any) -> Any:
    if isinstance(value, str):
        return unquote(value).replace("%3a", ":")
    return value


def _security_encode(password: str, key: str = AUTH_KEY, dictionary: str = AUTH_DICT) -> str:
    out: list[str] = []
    max_len = max(len(password), len(key))
    dict_len = len(dictionary)
    for idx in range(max_len):
        left = 187
        right = 187
        if idx >= len(password):
            right = ord(key[idx])
        elif idx >= len(key):
            left = ord(password[idx])
        else:
            left = ord(password[idx])
            right = ord(key[idx])
        out.append(dictionary[(left ^ right) % dict_len])
    return "".join(out)
