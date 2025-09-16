from __future__ import annotations

import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_DEFINITIONS, TEXT_SENSOR_DEFINITIONS
from .coordinator import VistaPoolCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: VistaPoolCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for sensor_id, definition in SENSOR_DEFINITIONS.items():
        entities.append(VistaPoolSensor(coordinator, sensor_id, definition, is_text=False))
    for sensor_id, definition in TEXT_SENSOR_DEFINITIONS.items():
        entities.append(VistaPoolSensor(coordinator, sensor_id, definition, is_text=True))

    async_add_entities(entities)


class VistaPoolSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, sensor_id: str, definition: dict, is_text: bool):
        super().__init__(coordinator)
        self._id = sensor_id
        self._definition = definition
        self._is_text = is_text

        self._attr_name = f"VistaPool {definition['name']}"
        self._attr_unique_id = f"{DOMAIN}_{sensor_id}"
        if not is_text:
            self._attr_native_unit_of_measurement = definition.get("unit")
            device_class = definition.get("device_class")
            if device_class:
                try:
                    self._attr_device_class = SensorDeviceClass(device_class)
                except Exception:
                    _LOGGER.warning("Invalid device_class %s for %s", device_class, sensor_id)

    @property
    def native_value(self):
        raw = self.coordinator.data
        path = self._definition["path"]
        value = raw.get(path.replace(".", "_"))
        if value is None:
            return None
        try:
            if self._is_text:
                return str(value)
            scale = self._definition.get("scale")
            if scale:
                return round(float(value) * scale, 2)
            return value
        except Exception:
            return value
