"""Constants for the network topology integration."""

DOMAIN = "network_topology"
API_PATH = "/api/network_topology/topology"
FRONTEND_URL = "/network_topology_static"
PANEL_URL_PATH = "network-topology"
PANEL_NAME = "network-topology"
PANEL_TITLE = "Network Topology"

CONF_ADAPTER = "adapter"
CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_ADAPTER = "tplink"
DEFAULT_HOST = "192.168.0.1"
DEFAULT_USERNAME = "root"
DEFAULT_SCAN_INTERVAL = 60

PLATFORMS = ["device_tracker"]
