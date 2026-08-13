"""Config flow for Network Topology."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries

from .adapters import ADAPTERS
from .const import (
    CONF_ADAPTER,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    DEFAULT_ADAPTER,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class NetworkTopologyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the network topology config flow."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return NetworkTopologyOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            adapter_key = user_input[CONF_ADAPTER]
            self.context["adapter_key"] = adapter_key
            return await self.async_step_adapter()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADAPTER, default=DEFAULT_ADAPTER): vol.In(
                        {key: adapter.label for key, adapter in ADAPTERS.items()}
                    )
                }
            ),
            errors=errors,
        )

    async def async_step_adapter(self, user_input: dict[str, Any] | None = None):
        adapter_key = self.context["adapter_key"]
        adapter_cls = ADAPTERS[adapter_key]
        errors: dict[str, str] = {}
        if user_input is not None:
            data = {CONF_ADAPTER: adapter_key, **user_input}
            data[CONF_SCAN_INTERVAL] = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            await self.async_set_unique_id(f"{adapter_key}:{data[CONF_HOST]}")
            self._abort_if_unique_id_configured()
            try:
                await _validate_input(self.hass, adapter_cls, data)
            except InvalidAuth:
                _LOGGER.warning(
                    "Network topology config validation failed: invalid auth adapter=%s host=%s",
                    adapter_key,
                    data[CONF_HOST],
                )
                errors["base"] = "invalid_auth"
            except CannotConnect:
                _LOGGER.warning(
                    "Network topology config validation failed: cannot connect adapter=%s host=%s",
                    adapter_key,
                    data[CONF_HOST],
                )
                errors["base"] = "cannot_connect"
            else:
                _LOGGER.debug(
                    "Network topology config validation succeeded adapter=%s host=%s",
                    adapter_key,
                    data[CONF_HOST],
                )
                return self.async_create_entry(title=f"{adapter_cls.label} {data[CONF_HOST]}", data=data)

        schema = adapter_cls.config_schema().extend(
            {
                vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=15),
                )
            }
        )
        return self.async_show_form(step_id="adapter", data_schema=schema, errors=errors)


class NetworkTopologyOptionsFlow(config_entries.OptionsFlow):
    """Handle editable options for an existing network topology entry."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        defaults = dict(self._config_entry.data)
        defaults.update(self._config_entry.options)
        adapter_cls = ADAPTERS[defaults[CONF_ADAPTER]]
        errors: dict[str, str] = {}
        if user_input is not None:
            merged = dict(defaults)
            merged.update(user_input)
            if not user_input.get(CONF_PASSWORD):
                merged[CONF_PASSWORD] = defaults[CONF_PASSWORD]
            try:
                await _validate_input(self.hass, adapter_cls, merged)
            except InvalidAuth:
                _LOGGER.warning(
                    "Network topology options validation failed: invalid auth adapter=%s host=%s",
                    defaults[CONF_ADAPTER],
                    merged[CONF_HOST],
                )
                errors["base"] = "invalid_auth"
            except CannotConnect:
                _LOGGER.warning(
                    "Network topology options validation failed: cannot connect adapter=%s host=%s",
                    defaults[CONF_ADAPTER],
                    merged[CONF_HOST],
                )
                errors["base"] = "cannot_connect"
            else:
                _LOGGER.debug(
                    "Network topology options validation succeeded adapter=%s host=%s",
                    defaults[CONF_ADAPTER],
                    merged[CONF_HOST],
                )
                options = dict(user_input)
                if not options.get(CONF_PASSWORD):
                    options.pop(CONF_PASSWORD, None)
                return self.async_create_entry(title="", data=options)

        schema = _options_schema(adapter_cls.config_schema(), defaults)
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)


async def _validate_input(hass, adapter_cls, data: dict[str, Any]) -> None:
    adapter = adapter_cls(
        hass=hass,
        **{
            key: value
            for key, value in data.items()
            if key not in {CONF_ADAPTER, CONF_SCAN_INTERVAL}
        },
    )
    try:
        await adapter.fetch()
    except Exception as exc:  # noqa: BLE001 - config flow maps transport errors to UI
        _LOGGER.debug(
            "Network topology adapter validation raised adapter=%s host=%s error_type=%s",
            data[CONF_ADAPTER],
            data[CONF_HOST],
            type(exc).__name__,
            exc_info=True,
        )
        if "authorize" in str(exc).lower() or "stok" in str(exc).lower():
            raise InvalidAuth from exc
        raise CannotConnect from exc


class CannotConnect(Exception):
    """Unable to connect to the network topology source."""


class InvalidAuth(Exception):
    """Invalid network topology source credentials."""


def _options_schema(schema: vol.Schema, defaults: dict[str, Any]) -> vol.Schema:
    """Make password optional in options while preserving adapter fields."""

    fields = dict(schema.schema)
    rebuilt: dict[Any, Any] = {}
    for key, validator in fields.items():
        raw_key = getattr(key, "schema", key)
        if raw_key == CONF_PASSWORD:
            rebuilt[vol.Optional(CONF_PASSWORD)] = validator
            continue
        if isinstance(raw_key, str):
            rebuilt[vol.Required(raw_key, default=defaults.get(raw_key))] = validator
            continue
        rebuilt[key] = validator
    fields = rebuilt
    password_field = next((key for key in fields if getattr(key, "schema", key) == CONF_PASSWORD), None)
    if password_field is not None:
        password_validator = fields.pop(password_field)
        fields[vol.Optional(CONF_PASSWORD)] = password_validator
    fields[
        vol.Required(
            CONF_SCAN_INTERVAL,
            default=defaults.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
    ] = vol.All(vol.Coerce(int), vol.Range(min=15))
    return vol.Schema(fields)
