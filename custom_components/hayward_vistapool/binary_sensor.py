from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, BINARY_SENSORS

_LOGGER = logging.getLogger(__name__)


@dataclass
class VistaPoolBinarySensorDescription(BinarySensorEntityDescription):
    key: str = ""


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [VistaPoolBinarySensor(coordinator, entry, VistaPoolBinarySensorDescription(**s)) for s in BINARY_SENSORS]
    async_add_entities(entities)


class VistaPoolBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, description: VistaPoolBinarySensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.data.get('pool_id')}_{description.key}"
        self._attr_name = description.name or description.key.replace("_", " ").title()
        if getattr(description, "icon", None):
            self._attr_icon = description.icon
        self._device_name = f"VistaPool {entry.data.get('pool_id')}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.data.get("pool_id"))},
            "name": self._device_name,
            "manufacturer": "Hayward",
            "model": "VistaPool WiFi Module",
            "sw_version": str(self.coordinator.data.get("main", {}).get("version")),
            "serial_number": str(self.coordinator.data.get("wifi")),
        }

    @property
    def is_on(self) -> bool:
        data = self.coordinator.data or {}
        key = self.entity_description.key
        if key not in data:
            _LOGGER.debug("VistaPool: binary sensor %s missing from coordinator data", key)
            return False

        raw = data.get(key)
        if raw in (None, "unknown", "unavailable", ""):
            _LOGGER.debug("VistaPool: binary sensor %s value is unavailable/unknown (%s)", key, raw)
            return False

        try:
            return int(raw) == 1
        except Exception as e:
            _LOGGER.warning("VistaPool: failed to parse binary %s value '%s' (%s)", key, raw, e)
            return str(raw).lower() in ("on", "true")
