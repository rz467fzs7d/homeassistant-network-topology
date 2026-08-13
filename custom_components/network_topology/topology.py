"""Build network topology payloads from normalized client devices."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any


def build_topology(
    *,
    devices: list[Any],
    root_label: str,
    root_ip: str,
    generated_at: str | None = None,
    source: str = "network-topology",
) -> dict[str, Any]:
    """Build the topology shape consumed by the frontend panel."""

    built_devices = [_build_device(device) for device in devices]
    built_devices = [device for device in built_devices if device is not None]

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for device in built_devices:
        grouped[device["group_id"]].append(device)

    group_ids = ["wired-lan", *sorted(group_id for group_id in grouped if group_id != "wired-lan")]
    groups = [
        {
            **_group(group_id),
            "device_count": len(grouped[group_id]),
        }
        for group_id in group_ids
        if group_id in grouped
    ]

    return {
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "source": source,
        "root": {
            "id": "network-root",
            "label": root_label,
            "ip": root_ip,
            "kind": "router",
        },
        "groups": groups,
        "devices": sorted(built_devices, key=lambda item: (item["group_id"], item["ip"])),
    }


def _build_device(device: Any) -> dict[str, Any] | None:
    if not bool(getattr(device, "online", True)):
        return None

    ip = str(getattr(device, "ip", "") or "").strip()
    mac = str(getattr(device, "mac", "") or "").strip()
    if not ip or not mac:
        return None

    ap_name = _clean(getattr(device, "ap_name", None))
    scope = "wireless" if ap_name else "wired"
    group_id = "wired-lan" if scope == "wired" else _group_id(ap_name)
    raw_name = str(getattr(device, "hostname", "") or "").strip()
    name = _fallback_name(raw_name, ip)
    signal = getattr(device, "signal", None)
    return {
        "id": f"device-{mac.lower()}",
        "name": name,
        "raw_name": raw_name,
        "ip": ip,
        "mac": mac,
        "scope": scope,
        "state": "online",
        "group_id": group_id,
        "access_point": "Wired LAN" if scope == "wired" else ap_name,
        "radio": _clean(getattr(device, "frequency", None)) or "",
        "ssid": _clean(getattr(device, "ssid", None)) or "",
        "rssi": f"{signal}dBm" if isinstance(signal, int) else "",
        "last_seen": "",
        "known": raw_name not in {"", "---", "anonymous", "wlan0", "lwip"},
    }


def _group(group_id: str) -> dict[str, str]:
    return {
        "id": group_id,
        "label": "Wired LAN" if group_id == "wired-lan" else _group_label(group_id),
        "kind": "wired" if group_id == "wired-lan" else "ap",
        "ip": "",
        "mac": "",
    }


def _fallback_name(raw_name: str, ip: str) -> str:
    if raw_name in {"", "---", "anonymous"}:
        return f"unknown-{ip}"
    if raw_name in {"wlan0", "lwip"}:
        return f"raw-{raw_name}-{ip}"
    return raw_name


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text == "---":
        return None
    return text


def _group_id(label: str) -> str:
    return label.lower().replace(" - ", "-").replace(" ", "-").replace("_", "-")


def _group_label(group_id: str) -> str:
    if group_id.startswith("ap-"):
        label = group_id.removeprefix("ap-").replace("-", " ")
        return "AP - " + label[:1].upper() + label[1:]
    return group_id.replace("-", " ").title()
