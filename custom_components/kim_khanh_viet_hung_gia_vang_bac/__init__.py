"""The Kim Khanh Viet Hung - Gia Vang Bac integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_SCAN_INTERVAL_HOURS,
    CONF_URL,
    COORDINATOR,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_URL,
    DOMAIN,
    SERVICE_REFRESH_PRICES,
)
from .coordinator import KimKhanhPriceCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Kim Khanh Viet Hung from a config entry."""
    url = entry.options.get(CONF_URL, entry.data.get(CONF_URL, DEFAULT_URL))
    scan_hours = entry.options.get(
        CONF_SCAN_INTERVAL_HOURS,
        entry.data.get(CONF_SCAN_INTERVAL_HOURS, int(DEFAULT_SCAN_INTERVAL.total_seconds() // 3600)),
    )
    update_interval = timedelta(hours=max(1, int(scan_hours)))

    coordinator = KimKhanhPriceCoordinator(
        hass=hass,
        entry=entry,
        url=url,
        update_interval=update_interval,
    )

    await coordinator.async_config_entry_first_refresh()
    if not coordinator.data:
        raise ConfigEntryNotReady("No price data returned from source")

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {COORDINATOR: coordinator}

    if not hass.services.has_service(DOMAIN, SERVICE_REFRESH_PRICES):

        async def _handle_refresh_service(call: ServiceCall) -> None:
            """Refresh all KHVH coordinators manually."""
            tasks = []
            for data in hass.data.get(DOMAIN, {}).values():
                svc_coordinator: KimKhanhPriceCoordinator = data[COORDINATOR]
                tasks.append(svc_coordinator.async_request_refresh())
            if tasks:
                await asyncio.gather(*tasks)

        hass.services.async_register(DOMAIN, SERVICE_REFRESH_PRICES, _handle_refresh_service)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
            if hass.services.has_service(DOMAIN, SERVICE_REFRESH_PRICES):
                hass.services.async_remove(DOMAIN, SERVICE_REFRESH_PRICES)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
