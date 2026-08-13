# Home Assistant Network Topology

[![Open your Home Assistant instance and open this repository inside HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=rz467fzs7d&repository=homeassistant-network-topology&category=integration)
[![Open your Home Assistant instance and start setting up Network Topology.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=network_topology)

Read-only Home Assistant custom integration for visualizing network client
topology and exposing client-to-access-point attachment as `device_tracker`
entities.

The first adapter targets TP-Link AC/AP routers via
[`tplinkrouterc6u`](https://pypi.org/project/tplinkrouterc6u/). The integration
is intentionally brand-neutral internally, so additional vendors can be added
through adapters without changing the frontend or entity model.

## Features

- HACS-compatible custom integration.
- Local polling through Home Assistant `DataUpdateCoordinator`.
- Topology JSON endpoint at `/api/network_topology/topology`.
- Sidebar panel at `/network-topology`.
- `device_tracker` entities for clients, including:
  - `ap_name`
  - `ssid`
  - `frequency`
  - `ip`
  - `signal_level`
- Raw RSSI remains in the topology JSON for visualization, but is not written
  as a recorder-heavy entity attribute.

## Installation

### HACS Custom Repository

1. Open HACS.
2. Go to **Integrations**.
3. Open the three-dot menu and choose **Custom repositories**.
4. Add this repository URL:

   ```text
   https://github.com/rz467fzs7d/homeassistant-network-topology
   ```

5. Select category **Integration**.
6. Install **Network Topology**.
7. Restart Home Assistant.
8. Add **Network Topology** from **Settings → Devices & services**.

### Manual

Copy this directory into your Home Assistant configuration directory:

```text
custom_components/network_topology
```

Then add the integration from the UI and restart Home Assistant if it does not
appear immediately.

The integration registers its own sidebar panel. You do not need a
`panel_custom` entry in `configuration.yaml`.

If you prefer YAML loading only, this minimal entry is enough:

```yaml
network_topology:
```

Restart Home Assistant after copying files.

## Configuration

The integration is configured through the UI.

For TP-Link routers:

- Host: router address reachable from Home Assistant
- Username: router web UI username
- Password: router web UI password
- Scan interval: polling interval in seconds

## Automation Example

```yaml
condition:
  - condition: state
    entity_id: device_tracker.nt_patricks_iphone
    attribute: ap_name
    state: "AP - Living room 01"
```

## Architecture

```text
Adapter
  -> DataUpdateCoordinator
      -> device_tracker entities
      -> topology store
          -> /api/network_topology/topology
          -> custom panel
```

Adapters normalize vendor-specific data into a shared `ClientDevice` model.
The frontend and entities consume the same coordinator data, so each poll logs
into the router only once.

## Current Adapter

### TP-Link

Uses `TPLinkRClient` from `tplinkrouterc6u==5.28.1`.

Supported fields:

- MAC address
- IP address
- hostname
- AP name
- SSID
- frequency
- RSSI
- online status

## Scope

This integration is read-only. It does not manage DHCP reservations, static IP
bindings, firewall rules, or router configuration.

## Development

Run local syntax checks:

```bash
python3 -m compileall custom_components
```

The integration is designed so adapter normalization and topology building can
be tested without a live router.
