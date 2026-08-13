"""Static TP-Link AC topology data for the Home Assistant panel."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any


RAW_TERMINALS: list[dict[str, str]] = [
    {'raw_name': 'anonymous', 'scope': 'wired', 'mac': 'FC-7C-02-EA-AF-73', 'ip': '192.168.0.2', 'access': '---', 'radio': '---', 'ssid': '---', 'rssi': '---', 'seen': '---', 'state': 'online'},
    {'raw_name': 'ds620slim', 'scope': 'wired', 'mac': '00-11-32-C9-24-0D', 'ip': '192.168.0.10', 'access': '---', 'radio': '---', 'ssid': '---', 'rssi': '---', 'seen': '---', 'state': 'online'},
    {'raw_name': 'n1b-homeassistant', 'scope': 'wired', 'mac': 'D2-F1-72-29-CF-5A', 'ip': '192.168.0.20', 'access': '---', 'radio': '---', 'ssid': '---', 'rssi': '---', 'seen': '---', 'state': 'online'},
    {'raw_name': 'mmm4', 'scope': 'wired', 'mac': 'D0-11-E5-78-11-DB', 'ip': '192.168.0.30', 'access': '---', 'radio': '---', 'ssid': '---', 'rssi': '---', 'seen': '---', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': 'E8-06-90-99-E6-B8', 'ip': '192.168.0.107', 'access': 'AP - Bedroom', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-25dBm', 'seen': '2026/06/07 15:33:07', 'state': 'online'},
    {'raw_name': 'PHICOMM-TC1-01', 'scope': 'wireless', 'mac': '3C-71-BF-2E-3B-A6', 'ip': '192.168.0.117', 'access': 'AP - Bedroom', 'radio': '2.4GHz', 'ssid': '11-1602, 2.4g', 'rssi': '-44dBm', 'seen': '2026/05/17 18:33:53', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': '58-B6-23-19-FE-67', 'ip': '192.168.0.119', 'access': 'AP - Bedroom', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-62dBm', 'seen': '2026/06/13 12:09:15', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': '20-43-A8-C5-B2-7C', 'ip': '192.168.0.121', 'access': 'AP - Bedroom', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-58dBm', 'seen': '2026/05/17 18:33:52', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': '54-48-E6-3E-2E-4D', 'ip': '192.168.0.122', 'access': 'AP - Bedroom', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-72dBm', 'seen': '2026/06/04 05:43:26', 'state': 'online'},
    {'raw_name': 'lwip', 'scope': 'wireless', 'mac': '38-1F-8D-7D-C4-2B', 'ip': '192.168.0.126', 'access': 'AP - Bedroom', 'radio': '2.4GHz', 'ssid': '11-1602, 2.4g', 'rssi': '-56dBm', 'seen': '2026/06/04 20:51:24', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': '34-19-4D-96-88-96', 'ip': '192.168.0.128', 'access': 'AP - Bedroom', 'radio': '5GHz', 'ssid': '11-1602, 5g', 'rssi': '-43dBm', 'seen': '2026/06/13 00:27:32', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': 'F4-34-F0-60-4A-2A', 'ip': '192.168.0.144', 'access': 'AP - Bedroom', 'radio': '5GHz', 'ssid': '11-1602', 'rssi': '-55dBm', 'seen': '2026/06/05 15:47:46', 'state': 'online'},
    {'raw_name': 'lwip', 'scope': 'wireless', 'mac': '38-1F-8D-7D-9C-3F', 'ip': '192.168.0.150', 'access': 'AP - Bedroom', 'radio': '2.4GHz', 'ssid': '11-1602, 2.4g', 'rssi': '-46dBm', 'seen': '2026/06/04 20:51:26', 'state': 'online'},
    {'raw_name': 'zhuwo', 'scope': 'wireless', 'mac': '48-E1-5C-6A-70-66', 'ip': '192.168.0.152', 'access': 'AP - Bedroom', 'radio': '5GHz', 'ssid': '11-1602, 5g', 'rssi': '-51dBm', 'seen': '2026/06/10 00:27:53', 'state': 'online'},
    {'raw_name': 'espressif', 'scope': 'wireless', 'mac': '84-0D-8E-2D-B7-78', 'ip': '192.168.0.157', 'access': 'AP - Bedroom', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-40dBm', 'seen': '2026/06/08 22:35:22', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': '20-43-A8-C5-BD-98', 'ip': '192.168.0.158', 'access': 'AP - Bedroom', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-56dBm', 'seen': '2026/05/29 21:52:25', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': '94-54-C5-D3-79-F8', 'ip': '192.168.0.161', 'access': 'AP - Bedroom', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-41dBm', 'seen': '2026/06/01 21:09:18', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': '38-42-0B-9C-40-72', 'ip': '192.168.0.163', 'access': 'AP - Bedroom', 'radio': '5GHz', 'ssid': '11-1602, 5g', 'rssi': '-41dBm', 'seen': '2026/05/17 18:34:28', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': '38-42-0B-9C-40-7A', 'ip': '192.168.0.164', 'access': 'AP - Bedroom', 'radio': '5GHz', 'ssid': '11-1602, 5g', 'rssi': '-41dBm', 'seen': '2026/05/17 18:34:28', 'state': 'online'},
    {'raw_name': 'mac-mini-m4-wlan', 'scope': 'wireless', 'mac': '36-6F-FE-9F-07-AA', 'ip': '192.168.0.31', 'access': 'AP - Dining room', 'radio': '5GHz', 'ssid': '11-1602, 5g', 'rssi': '-52dBm', 'seen': '2026/06/10 22:06:08', 'state': 'online'},
    {'raw_name': 'lumi_gateway_mgl03', 'scope': 'wireless', 'mac': '54-EF-44-22-6A-8D', 'ip': '192.168.0.109', 'access': 'AP - Dining room', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-48dBm', 'seen': '2026/04/18 18:44:24', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': '04-99-B9-78-12-4B', 'ip': '192.168.0.142', 'access': 'AP - Dining room', 'radio': '5GHz', 'ssid': '11-1602, 5g', 'rssi': '-44dBm', 'seen': '2026/06/05 19:48:58', 'state': 'online'},
    {'raw_name': 'PHICOMM-TC1-02', 'scope': 'wireless', 'mac': '3C-71-BF-2E-3A-4B', 'ip': '192.168.0.143', 'access': 'AP - Dining room', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-28dBm', 'seen': '2026/04/30 23:16:44', 'state': 'online'},
    {'raw_name': 'yeelink-light-ceiling1_mibt5A5B', 'scope': 'wireless', 'mac': '34-CE-00-8C-5A-5B', 'ip': '192.168.0.115', 'access': 'AP - Kidsroom', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-45dBm', 'seen': '2026/06/04 20:50:12', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': '3C-71-BF-2E-3A-BA', 'ip': '192.168.0.162', 'access': 'AP - Kidsroom', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-33dBm', 'seen': '2026/05/30 19:58:58', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': '54-EF-44-87-1A-33', 'ip': '192.168.0.167', 'access': 'AP - Kidsroom', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-36dBm', 'seen': '2026/04/30 23:19:52', 'state': 'online'},
    {'raw_name': 'wlan0', 'scope': 'wireless', 'mac': 'A8-40-7D-4D-60-9F', 'ip': '192.168.0.169', 'access': 'AP - Kidsroom', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-58dBm', 'seen': '2026/06/13 09:45:29', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': '8C-DE-F9-84-C6-00', 'ip': '192.168.0.120', 'access': 'AP - Living room 01', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-31dBm', 'seen': '2026/06/04 21:28:25', 'state': 'online'},
    {'raw_name': 'roborock-vacuum-a143', 'scope': 'wireless', 'mac': 'B0-4A-39-F9-02-8D', 'ip': '192.168.0.151', 'access': 'AP - Living room 01', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-55dBm', 'seen': '2026/06/15 03:53:38', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': '54-EF-44-8B-AD-65', 'ip': '192.168.0.166', 'access': 'AP - Living room 01', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-24dBm', 'seen': '2026/04/25 04:23:42', 'state': 'online'},
    {'raw_name': 'dietpi', 'scope': 'wireless', 'mac': '2A-6F-C9-29-99-01', 'ip': '192.168.0.40', 'access': 'AP - Living room 02', 'radio': '5GHz', 'ssid': '11-1602', 'rssi': '-71dBm', 'seen': '2026/06/13 10:34:35', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': 'C0-95-6D-59-8A-FC', 'ip': '192.168.0.112', 'access': 'AP - Living room 02', 'radio': '5GHz', 'ssid': '11-1602', 'rssi': '-59dBm', 'seen': '2026/06/12 22:51:51', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': '78-11-DC-68-F7-C3', 'ip': '192.168.0.113', 'access': 'AP - Living room 02', 'radio': '2.4GHz', 'ssid': '11-1602, 2.4g', 'rssi': '-42dBm', 'seen': '2026/06/04 20:51:31', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': '3C-71-BF-2E-3A-C0', 'ip': '192.168.0.118', 'access': 'AP - Living room 02', 'radio': '2.4GHz', 'ssid': '11-1602', 'rssi': '-37dBm', 'seen': '2026/05/17 18:33:53', 'state': 'online'},
    {'raw_name': 'anonymous', 'scope': 'wireless', 'mac': '78-11-DC-39-E9-C5', 'ip': '192.168.0.127', 'access': 'AP - Living room 02', 'radio': '2.4GHz', 'ssid': '11-1602, 2.4g', 'rssi': '-44dBm', 'seen': '2026/05/17 18:34:25', 'state': 'online'},
    {'raw_name': 'wlan0', 'scope': 'wireless', 'mac': '50-8B-B9-5B-31-35', 'ip': '192.168.0.129', 'access': 'AP - Living room 02', 'radio': '2.4GHz', 'ssid': '11-1602, 2.4g', 'rssi': '-64dBm', 'seen': '2026/06/04 20:51:19', 'state': 'online'},
    {'raw_name': 'm4-mac-mini', 'scope': 'wireless', 'mac': 'AC-BC-B5-E9-0D-DE', 'ip': '192.168.0.133', 'access': 'AP - Living room 02', 'radio': '5GHz', 'ssid': '11-1602, 5g', 'rssi': '-46dBm', 'seen': '2026/06/12 22:49:34', 'state': 'online'},
    {'raw_name': 'wlan0', 'scope': 'wireless', 'mac': '50-8B-B9-5B-21-D6', 'ip': '192.168.0.145', 'access': 'AP - Living room 02', 'radio': '2.4GHz', 'ssid': '11-1602, 2.4g', 'rssi': '-66dBm', 'seen': '2026/06/04 20:51:18', 'state': 'online'},
    {'raw_name': 'wlan0', 'scope': 'wireless', 'mac': '50-8B-B9-5B-19-D8', 'ip': '192.168.0.146', 'access': 'AP - Living room 02', 'radio': '2.4GHz', 'ssid': '11-1602, 2.4g', 'rssi': '-77dBm', 'seen': '2026/06/04 20:51:18', 'state': 'online'},
    {'raw_name': 'wlan0', 'scope': 'wireless', 'mac': '50-8B-B9-5B-2E-6B', 'ip': '192.168.0.154', 'access': 'AP - Living room 02', 'radio': '2.4GHz', 'ssid': '11-1602, 2.4g', 'rssi': '-74dBm', 'seen': '2026/06/04 20:51:18', 'state': 'online'},
    {'raw_name': 'wlan0', 'scope': 'wireless', 'mac': '50-8B-B9-5B-1D-C6', 'ip': '192.168.0.155', 'access': 'AP - Living room 02', 'radio': '2.4GHz', 'ssid': '11-1602, 2.4g', 'rssi': '-73dBm', 'seen': '2026/06/04 20:36:18', 'state': 'online'},
]


NAME_OVERRIDES_BY_IP: dict[str, str] = {
    '192.168.0.2': 'OpenWrt',
    '192.168.0.10': 'NAS DS620slim',
    '192.168.0.20': 'Home Assistant',
    '192.168.0.30': 'Mac mini M4 (LAN)',
    '192.168.0.31': 'Mac mini M4 (Wi-Fi)',
    '192.168.0.40': 'DietPi',
    '192.168.0.105': 'Candices-iPad',
    '192.168.0.107': 'Bambu A1 mini',
    '192.168.0.108': 'Mr.Bond Airer',
    '192.168.0.109': 'Xiaomi Gateway',
    '192.168.0.113': 'Yeelight Ceiling Light 3',
    '192.168.0.114': 'Candice Watch',
    '192.168.0.115': 'Yeelight Ceiling Light 1',
    '192.168.0.117': 'PHICOMM-TC1-01',
    '192.168.0.118': 'PHICOMM-TC1-04',
    '192.168.0.120': 'Xiaomi Speaker',
    '192.168.0.121': 'Toilet Seat',
    '192.168.0.122': 'Yunmi Water Purifier',
    '192.168.0.125': 'Apple TV Living Room',
    '192.168.0.127': 'Xiaomi Camera',
    '192.168.0.133': 'Living-Room',
    '192.168.0.140': 'HomePod R',
    '192.168.0.141': 'HomePod-L',
    '192.168.0.142': 'HomePod-mini',
    '192.168.0.143': 'PHICOMM-TC1-02',
    '192.168.0.144': 'HomePod-mini-2',
    '192.168.0.151': 'Roborock',
    '192.168.0.158': 'Light Strip',
    '192.168.0.160': 'LG Smart Laundry',
    '192.168.0.161': 'PURA MAX 2',
    '192.168.0.162': 'PHICOMM-TC1-03',
    '192.168.0.163': 'Sonos Stereo Right',
    '192.168.0.164': 'Sonos Stereo Left',
    '192.168.0.166': 'Aqara Camera G100 02',
    '192.168.0.167': 'Aqara Camera G100 01',
    '192.168.0.168': 'Chunmi Rice Cooker',
    '192.168.0.169': 'Midea Dishwasher',
}


KNOWN_GROUPS: list[dict[str, str]] = [
    {'id': 'wired-lan', 'label': 'Wired LAN', 'kind': 'wired', 'ip': ''},
    {'id': 'ap-bedroom', 'label': 'AP - Bedroom', 'kind': 'ap', 'ip': '192.168.0.135', 'mac': '3C-06-A7-88-03-A5'},
    {'id': 'ap-dining-room', 'label': 'AP - Dining room', 'kind': 'ap', 'ip': '192.168.0.136', 'mac': '3C-06-A7-4C-B6-19'},
    {'id': 'ap-kidsroom', 'label': 'AP - Kidsroom', 'kind': 'ap', 'ip': '192.168.0.132', 'mac': '3C-06-A7-4C-B1-E7'},
    {'id': 'ap-living-room-01', 'label': 'AP - Living room 01', 'kind': 'ap', 'ip': '192.168.0.123', 'mac': 'EC-60-73-CE-71-A1'},
    {'id': 'ap-living-room-02', 'label': 'AP - Living room 02', 'kind': 'ap', 'ip': '192.168.0.134', 'mac': '3C-06-A7-4C-AE-2D'},
]


GROUP_ORDER = [group["id"] for group in KNOWN_GROUPS]


def build_static_topology() -> dict[str, Any]:
    """Build topology data from the refreshed TP-Link terminal-management snapshot."""

    devices = [_build_device(row) for row in RAW_TERMINALS]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for device in devices:
        grouped[device["group_id"]].append(device)

    known_group_by_id = {group["id"]: group for group in KNOWN_GROUPS}
    group_ids = [*GROUP_ORDER, *sorted(set(grouped) - set(GROUP_ORDER))]
    groups = [
        {
            "id": group_id,
            "label": known_group_by_id.get(group_id, {}).get("label") or _group_label(group_id),
            "kind": known_group_by_id.get(group_id, {}).get("kind") or ("wired" if group_id == "wired-lan" else "ap"),
            "ip": known_group_by_id.get(group_id, {}).get("ip", ""),
            "mac": known_group_by_id.get(group_id, {}).get("mac", ""),
            "device_count": len(grouped[group_id]),
        }
        for group_id in group_ids
        if group_id in grouped or group_id in known_group_by_id
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "tplink-web-host-management-snapshot",
        "root": {
            "id": "tplink-ac",
            "label": "TL-R489GP-AC",
            "ip": "192.168.0.1",
            "kind": "router-ac",
        },
        "groups": groups,
        "devices": devices,
    }


def _build_device(row: dict[str, str]) -> dict[str, Any]:
    group_id = "wired-lan" if row["scope"] == "wired" else _slugify_ap(row["access"])
    raw_name = row["raw_name"]
    name = NAME_OVERRIDES_BY_IP.get(row["ip"]) or _fallback_name(raw_name, row["ip"])
    return {
        "id": row["mac"].lower(),
        "name": name,
        "raw_name": raw_name,
        "ip": row["ip"],
        "mac": row["mac"],
        "scope": row["scope"],
        "state": row.get("state", ""),
        "group_id": group_id,
        "access_point": "Wired LAN" if row["scope"] == "wired" else row["access"],
        "radio": "" if row["radio"] == "---" else row["radio"],
        "ssid": "" if row["ssid"] == "---" else row["ssid"],
        "rssi": "" if row["rssi"] == "---" else row["rssi"],
        "last_seen": "" if row["seen"] == "---" else row["seen"],
        "known": row["ip"] in NAME_OVERRIDES_BY_IP or raw_name not in {"---", "anonymous", "wlan0", "lwip"},
    }


def _fallback_name(raw_name: str, ip: str) -> str:
    if raw_name in {"---", "anonymous"}:
        return f"unknown-{ip}"
    if raw_name in {"wlan0", "lwip"}:
        return f"raw-{raw_name}-{ip}"
    return raw_name


def _slugify_ap(access: str) -> str:
    return "ap-" + access.removeprefix("AP - ").lower().replace(" ", "-")


def _group_label(group_id: str) -> str:
    if group_id == "wired-lan":
        return "Wired LAN"
    return "AP - " + group_id.removeprefix("ap-").replace("-", " ").title().replace("Room", "room")
