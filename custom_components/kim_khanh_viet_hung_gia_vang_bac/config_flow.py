"""Config flow for Kim Khanh Viet Hung - Gia Vang Bac integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_SCAN_INTERVAL_HOURS,
    CONF_URL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_URL,
    DOMAIN,
)


class KimKhanhConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Kim Khanh Viet Hung - Gia Vang Bac."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Kim Khánh Việt Hùng", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(CONF_URL, default=DEFAULT_URL): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL_HOURS,
                    default=int(DEFAULT_SCAN_INTERVAL.total_seconds() // 3600),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=168)),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return KimKhanhOptionsFlow(config_entry)


class KimKhanhOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_URL,
                    default=self._config_entry.options.get(
                        CONF_URL,
                        self._config_entry.data.get(CONF_URL, DEFAULT_URL),
                    ),
                ): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL_HOURS,
                    default=self._config_entry.options.get(
                        CONF_SCAN_INTERVAL_HOURS,
                        self._config_entry.data.get(
                            CONF_SCAN_INTERVAL_HOURS,
                            int(DEFAULT_SCAN_INTERVAL.total_seconds() // 3600),
                        ),
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=168)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
