from __future__ import annotations

import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, BINARY_SENSOR_DEFINITIONS
from .coordinator import VistaPoolCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: VistaPoolCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [VistaPoolBinarySensor(coordinator, sensor_id, definition)
                for sensor_id, definition in BINARY_SENSOR_DEFINITIONS.items()]
    async_add_entities(entities)


class VistaPoolBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, sensor_id: str, definition: dict):
        super().__init__(coordinator)
        self._definition = definition
        self._id = sensor_id
        self._attr_name = f"VistaPool {definition['name']}"
        self._attr_unique_id = f"{DOMAIN}_{sensor_id}"

    @property
    def is_on(self):
        raw = self.coordinator.data
        path = self._definition["path"]
        value = raw.get(path.replace(".", "_"))
        if value is None:
            return None
        try:
            return bool(int(value))
        except Exception:
            return bool(value)
