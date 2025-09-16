from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .coordinator import VistaPoolCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor", "binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hayward VistaPool from a config entry."""
    email = entry.data["email"]
    password = entry.data["password"]
    pool_id = entry.data["pool_id"]

    scan_interval = entry.data.get("scan_interval", entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL))
    enable_debug = entry.data.get("enable_debug", entry.options.get("enable_debug", False))

    _LOGGER.info(
        "Setting up VistaPool (pool_id=%s, scan_interval=%s, debug=%s)",
        pool_id, scan_interval, enable_debug,
    )

    coordinator = VistaPoolCoordinator(
        hass,
        email=email,
        password=password,
        pool_id=pool_id,
        scan_interval=scan_interval,
        enable_debug=enable_debug,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
