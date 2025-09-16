from __future__ import annotations

DOMAIN = "hayward_vistapool"
DEFAULT_SCAN_INTERVAL = 1800  # default 30 minutes

API_KEY = "AIzaSyBLaxiyZ2nS1KgRBqWe-NY4EG7OzG5fKpE"
FIREBASE_LOGIN_URL = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEY}"
FIRESTORE_URL = "https://firestore.googleapis.com/v1/projects/hayward-europe/databases/(default)/documents/pools/{pool_id}"

# ✅ Numeric sensors
SENSOR_DEFINITIONS = {
    "water_temperature": {
        "path": "main.temperature",
        "name": "Water Temperature",
        "unit": "°C",
        "device_class": "temperature",
    },
    "ph_current": {
        "path": "modules.ph.current",
        "name": "pH Current",
        "unit": "pH",
        "scale": 0.01,
    },
    "orp": {
        "path": "modules.rx.status.value",
        "name": "ORP",
        "unit": "mV",
    },
    "salt_level": {
        "path": "hidro.level",
        "name": "Salt Level",
    },
    "salt_cell_total_runtime": {
        "path": "hidro.cellTotalTime",
        "name": "Salt Cell Runtime (Total)",
        "unit": "h",
        "scale": 1 / 3600,
    },
    "salt_cell_partial_runtime": {
        "path": "hidro.cellPartialTime",
        "name": "Salt Cell Runtime (Partial)",
        "unit": "h",
        "scale": 1 / 3600,
    },
    "filtration_intel_temp": {
        "path": "filtration.intel.temp",
        "name": "Filtration Intel Temp",
        "unit": "°C",
    },
    "filtration_heating_temp": {
        "path": "filtration.heating.temp",
        "name": "Filtration Heating Temp",
        "unit": "°C",
    },
    "filtration_smart_min_temp": {
        "path": "filtration.smart.tempMin",
        "name": "Filtration Smart Min Temp",
        "unit": "°C",
    },
    "filtration_smart_max_temp": {
        "path": "filtration.smart.tempHigh",
        "name": "Filtration Smart Max Temp",
        "unit": "°C",
    },
    "wifi_signal_strength": {
        "path": "main.RSSI",
        "name": "WiFi Signal Strength",
        "unit": "dBm",
        "device_class": "signal_strength",
    },
}

# ✅ Text sensors
TEXT_SENSOR_DEFINITIONS = {
    "ph_low_setpoint": {
        "path": "modules.ph.status.low_value",
        "name": "pH Low Setpoint",
    },
    "ph_high_setpoint": {
        "path": "modules.ph.status.high_value",
        "name": "pH High Setpoint",
    },
    "chlorine_status": {
        "path": "modules.cl.status.value",
        "name": "Chlorine Status",
    },
    "ph_type": {
        "path": "modules.ph.type",
        "name": "pH Type",
    },
    "firmware_version": {
        "path": "main.version",
        "name": "Controller Firmware Version",
    },
    "wifi_version": {
        "path": "main.wifiVersion",
        "name": "WiFi Firmware Version",
    },
}

# ✅ Binary sensors
BINARY_SENSOR_DEFINITIONS = {
    "filtration_running": {
        "path": "filtration.status",
        "name": "Filtration Running",
    },
    "light_on": {
        "path": "light.status",
        "name": "Light On",
    },
    "salt_electrolysis_active": {
        "path": "hidro.is_electrolysis",
        "name": "Salt Electrolysis Active",
    },
    "uv_lamp_status": {
        "path": "modules.uv.status",
        "name": "UV Lamp Status",
    },
    "backwash_active": {
        "path": "backwash.status",
        "name": "Backwash Active",
    },
    "controller_present": {
        "path": "present",
        "name": "Controller Present",
    },
    "network_present": {
        "path": "main.networkPresent",
        "name": "Network Present",
    },
}
