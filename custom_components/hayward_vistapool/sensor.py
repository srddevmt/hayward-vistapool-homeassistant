from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSORS

_LOGGER = logging.getLogger(__name__)


@dataclass
class VistaPoolSensorDescription(SensorEntityDescription):
    key: str = ""


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [VistaPoolSensor(coordinator, entry, VistaPoolSensorDescription(**s)) for s in SENSORS]
    async_add_entities(entities)


class VistaPoolSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, description: VistaPoolSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.data.get('pool_id')}_{description.key}"
        self._attr_name = description.name or description.key.replace("_", " ").title()
        if getattr(description, "icon", None):
            self._attr_icon = description.icon
        if getattr(description, "device_class", None):
            self._attr_device_class = description.device_class
        if getattr(description, "state_class", None):
            self._attr_state_class = description.state_class
        if getattr(description, "native_unit_of_measurement", None):
            self._attr_native_unit_of_measurement = description.native_unit_of_measurement
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
    def available(self) -> bool:
        data = self.coordinator.data or {}
        return self.entity_description.key in data

    @property
    def native_value(self) -> Any:
        data = self.coordinator.data or {}
        key = self.entity_description.key
        if key not in data:
            _LOGGER.debug("VistaPool: %s missing from coordinator data", key)
            return None

        raw = data.get(key)

        if raw in (None, "unknown", "Unknown", "unavailable", ""):
            _LOGGER.debug("VistaPool: %s value is unavailable/unknown (%s)", key, raw)
            return None

        try:
            if key == "ph":
                val = float(raw)
                return round(val / 100.0, 2) if val > 14 else round(val, 2)

            if key == "chlorine_production":
                max_allowed = data.get("maxAllowedValue") or data.get("chlorine_production_max") or 100
                return round((float(raw) / float(max_allowed)) * 100.0, 1)

            return float(raw)
        except Exception as e:
            _LOGGER.warning("VistaPool: failed to parse %s value '%s' (%s)", key, raw, e)
            try:
                return str(raw)
            except Exception:
                return None
