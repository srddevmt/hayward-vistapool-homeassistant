from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .coordinator import VistaPoolCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hayward VistaPool from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    email = entry.data.get("email")
    password = entry.data.get("password")
    pool_id = entry.data.get("pool_id")

    session = async_get_clientsession(hass)
    scan_interval = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)

    coordinator = VistaPoolCoordinator(
        hass, session, email, password, pool_id, scan_interval=scan_interval
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
