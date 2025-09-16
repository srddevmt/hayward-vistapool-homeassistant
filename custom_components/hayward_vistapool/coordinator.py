from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict

import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, FIREBASE_LOGIN_URL, FIRESTORE_URL

_LOGGER = logging.getLogger(__name__)


def _coerce_firestore_value(v: Dict[str, Any]) -> Any:
    """Convert Firestore-typed values into native Python types."""
    if not isinstance(v, dict):
        return v
    for k in ("doubleValue", "integerValue", "stringValue", "booleanValue"):
        if k in v:
            val = v[k]
            try:
                if k == "integerValue":
                    return int(val)
                if k == "doubleValue":
                    return float(val)
                if k == "booleanValue":
                    return bool(val)
                return val  # stringValue
            except Exception as e:
                _LOGGER.debug("Failed to coerce Firestore value %s: %s", val, e)
                return val
    if "mapValue" in v and "fields" in v["mapValue"]:
        return {kk: _coerce_firestore_value(vv) for kk, vv in v["mapValue"]["fields"].items()}
    if "arrayValue" in v and "values" in v["arrayValue"]:
        return [_coerce_firestore_value(x) for x in v["arrayValue"]["values"]]
    return v


class VistaPoolCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Coordinator to fetch data from VistaPool cloud."""

    def __init__(self, hass, session: aiohttp.ClientSession, email: str, password: str, pool_id: str, scan_interval: int = 600) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=scan_interval))
        self._session = session
        self.email = email
        self.password = password
        self.pool_id = pool_id
        self.id_token: str | None = None

    async def _async_login(self) -> None:
        """Log in to Firebase and store ID token."""
        payload = {"email": self.email, "password": self.password, "returnSecureToken": True}
        _LOGGER.debug("VistaPool: attempting login for %s", self.email)
        async with self._session.post(FIREBASE_LOGIN_URL, json=payload) as resp:
            data = await resp.json()
            if resp.status != 200 or "idToken" not in data:
                _LOGGER.error("VistaPool login failed (status %s): %s", resp.status, data)
                raise UpdateFailed(f"Login failed: {data.get('error', data)}")
            self.id_token = data["idToken"]
            _LOGGER.debug("VistaPool: login successful, idToken acquired")

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch the latest pool data from Firestore."""
        try:
            if not self.id_token:
                _LOGGER.debug("VistaPool: no idToken, logging in")
                await self._async_login()

            headers = {"Authorization": f"Bearer {self.id_token}"}
            url = FIRESTORE_URL.format(pool_id=self.pool_id)

            _LOGGER.debug("VistaPool: fetching data for pool_id=%s", self.pool_id)
            async with self._session.get(url, headers=headers) as resp:
                if resp.status == 401:
                    _LOGGER.warning("VistaPool: token expired, re-logging in")
                    await self._async_login()
                    headers = {"Authorization": f"Bearer {self.id_token}"}
                    resp = await self._session.get(url, headers=headers)

                raw = await resp.json()
                if resp.status != 200 or "fields" not in raw:
                    _LOGGER.error("VistaPool: bad response %s - %s", resp.status, raw)
                    raise UpdateFailed(f"Bad response: {raw}")

                _LOGGER.debug("VistaPool: raw payload received (truncated): %s", str(raw)[:500])

                fields = {k: _coerce_firestore_value(v) for k, v in raw["fields"].items()}

                _LOGGER.debug("VistaPool: parsed fields: %s", fields)

                return fields

        except Exception as err:
            _LOGGER.exception("VistaPool: error fetching data")
            raise UpdateFailed(f"Error fetching VistaPool data: {err}") from err
