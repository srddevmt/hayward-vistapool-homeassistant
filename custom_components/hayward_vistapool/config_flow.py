from __future__ import annotations

import logging
import voluptuous as vol
from aiohttp import ClientSession

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, FIREBASE_LOGIN_URL, FIRESTORE_URL

_LOGGER = logging.getLogger(__name__)

# Human-friendly scan intervals
SCAN_INTERVALS = {
    "10 minutes": 600,
    "30 minutes": 1800,
    "1 hour": 3600,
    "6 hours": 21600,
    "12 hours": 43200,
    "1 day": 86400,
}


async def _async_try_login(hass: HomeAssistant, email: str, password: str, pool_id: str) -> bool:
    """Try to login to VistaPool Firebase and fetch pool data once."""
    try:
        async with ClientSession() as session:
            payload = {"email": email, "password": password, "returnSecureToken": True}
            async with session.post(FIREBASE_LOGIN_URL, json=payload) as resp:
                data = await resp.json()
                if resp.status != 200 or "idToken" not in data:
                    _LOGGER.error("VistaPool: login failed during config flow: %s", data)
                    return False
                id_token = data["idToken"]

            headers = {"Authorization": f"Bearer {id_token}"}
            url = FIRESTORE_URL.format(pool_id=pool_id)
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                if resp.status != 200 or "fields" not in data:
                    _LOGGER.error("VistaPool: Firestore fetch failed during config flow: %s", data)
                    return False

        return True
    except Exception as e:
        _LOGGER.exception("VistaPool: exception in _async_try_login: %s", e)
        return False


class VistaPoolConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hayward VistaPool."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        # Build schema using vol.In() for dropdown
        data_schema = vol.Schema(
            {
                vol.Required("email"): str,
                vol.Required("password"): str,
                vol.Required("pool_id"): str,
                vol.Optional("scan_interval", default=1800): vol.In(SCAN_INTERVALS),
                vol.Optional("enable_debug", default=False): bool,
            }
        )

        if user_input is not None:
            email = user_input["email"]
            password = user_input["password"]
            pool_id = user_input["pool_id"]
            scan_label = user_input["scan_interval"]
            enable_debug = user_input["enable_debug"]

            scan_interval = SCAN_INTERVALS.get(scan_label, 1800)

            ok = await _async_try_login(self.hass, email, password, pool_id)
            if ok:
                await self.async_set_unique_id(pool_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"VistaPool {pool_id}",
                    data={
                        "email": email,
                        "password": password,
                        "pool_id": pool_id,
                        "scan_interval": scan_interval,
                        "enable_debug": enable_debug,
                    },
                )
            errors["base"] = "auth"

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return VistaPoolOptionsFlowHandler(config_entry)


class VistaPoolOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle VistaPool options (e.g., scan interval, debug logging)."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        super().__init__()
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        if user_input is not None:
            scan_label = user_input["scan_interval"]
            scan_interval = SCAN_INTERVALS.get(scan_label, 1800)
            return self.async_create_entry(
                title="",
                data={
                    "scan_interval": scan_interval,
                    "enable_debug": user_input["enable_debug"],
                },
            )

        # Reverse lookup current interval
        current_interval = self._config_entry.options.get(
            "scan_interval", self._config_entry.data.get("scan_interval", 1800)
        )
        default_label = next(
            (label for label, seconds in SCAN_INTERVALS.items() if seconds == current_interval),
            "30 minutes",
        )

        data_schema = vol.Schema(
            {
                vol.Optional("scan_interval", default=default_label): vol.In(SCAN_INTERVALS),
                vol.Optional(
                    "enable_debug",
                    default=self._config_entry.options.get(
                        "enable_debug", self._config_entry.data.get("enable_debug", False)
                    ),
                ): bool,
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
