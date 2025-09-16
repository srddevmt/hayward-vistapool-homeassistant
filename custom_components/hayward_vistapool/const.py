from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

DOMAIN = "hayward_vistapool"
DEFAULT_SCAN_INTERVAL = 600  # seconds (10 minutes by default)

FIREBASE_LOGIN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=YOUR_FIREBASE_API_KEY"
FIRESTORE_URL = "https://firestore.googleapis.com/v1/projects/YOUR_PROJECT_ID/databases/(default)/documents/pools/{pool_id}"

# Standard sensors (numeric / measurement)
SENSORS = [
    {"key": "water_temperature", "name": "Water Temperature", "device_class": SensorDeviceClass.TEMPERATURE, "state_class": SensorStateClass.MEASUREMENT, "native_unit_of_measurement": "°C", "icon": "mdi:coolant-temperature"},
    {"key": "ph", "name": "pH Level", "state_class": SensorStateClass.MEASUREMENT, "native_unit_of_measurement": "pH", "icon": "mdi:alpha-p-circle"},
    {"key": "chlorine", "name": "Chlorine Level", "state_class": SensorStateClass.MEASUREMENT, "native_unit_of_measurement": "mg/L", "icon": "mdi:flask-outline"},
    {"key": "chlorine_production", "name": "Chlorine Production", "state_class": SensorStateClass.MEASUREMENT, "native_unit_of_measurement": "%", "icon": "mdi:gauge"},
    {"key": "orp", "name": "Oxidation Reduction Potential", "state_class": SensorStateClass.MEASUREMENT, "native_unit_of_measurement": "mV", "icon": "mdi:flash"},
    {"key": "conductivity", "name": "Conductivity", "state_class": SensorStateClass.MEASUREMENT, "native_unit_of_measurement": "µS/cm", "icon": "mdi:water-check"},
    {"key": "heating_setpoint", "name": "Heating Setpoint", "device_class": SensorDeviceClass.TEMPERATURE, "native_unit_of_measurement": "°C", "icon": "mdi:thermometer-plus"},
    {"key": "uv_runtime", "name": "UV Runtime", "state_class": SensorStateClass.TOTAL_INCREASING, "native_unit_of_measurement": "h", "icon": "mdi:timer-outline"},
    {"key": "ph_tank_level", "name": "pH Tank Level", "native_unit_of_measurement": "%", "icon": "mdi:beaker-outline"},
    {"key": "cl_tank_level", "name": "Chlorine Tank Level", "native_unit_of_measurement": "%", "icon": "mdi:beaker-outline"},
    {"key": "water_level", "name": "Water Level", "native_unit_of_measurement": "%", "icon": "mdi:waves"},
    {"key": "cell_partial_time", "name": "Cell Partial Time", "state_class": SensorStateClass.TOTAL_INCREASING, "native_unit_of_measurement": "s", "icon": "mdi:timer-sand"},
    {"key": "cell_total_time", "name": "Cell Total Time", "state_class": SensorStateClass.TOTAL_INCREASING, "native_unit_of_measurement": "s", "icon": "mdi:timer"},
    {"key": "wifi_signal", "name": "WiFi Signal", "device_class": SensorDeviceClass.SIGNAL_STRENGTH, "state_class": SensorStateClass.MEASUREMENT, "native_unit_of_measurement": "dBm", "icon": "mdi:wifi"},
    {"key": "rssi", "name": "Signal Strength (RSSI)", "device_class": SensorDeviceClass.SIGNAL_STRENGTH, "state_class": SensorStateClass.MEASUREMENT, "native_unit_of_measurement": "dBm", "icon": "mdi:wifi-strength-2"},
]

# Binary sensors (on/off)
BINARY_SENSORS = [
    {"key": "filtration", "name": "Filtration Running", "device_class": "running", "icon": "mdi:filter"},
    {"key": "flow_status", "name": "Flow Detected", "device_class": "problem", "icon": "mdi:pipe"},
    {"key": "uv_status", "name": "UV System", "device_class": "power", "icon": "mdi:lightbulb-on"},
    {"key": "ph_pump_status", "name": "pH Pump", "device_class": "power", "icon": "mdi:pump"},
    {"key": "cl_pump_status", "name": "Chlorine Pump", "device_class": "power", "icon": "mdi:pump"},
]
