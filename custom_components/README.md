Hayward VistaPool Home Assistant Integration

Custom integration for Home Assistant
 that connects your Hayward VistaPool / PoolWatch WiFi module to Home Assistant via Firebase + Firestore.

Developed by Searise Developments Ltd. (MIT License)

✨ Features

Monitors pool chemistry:

Water Temperature
pH
Chlorine (mg/L)
ORP (mV)
Conductivity
Chlorine Production %

Tracks equipment runtime:
Cell Partial/Total Time
UV Runtime

Tank levels & water level:
pH Tank Level
Chlorine Tank Level
Water Level

Binary status sensors:
Filtration Running
Flow Detected
UV System
pH Pump
Chlorine Pump

Connectivity:
WiFi Signal
RSSI

Enriched device information:
Manufacturer: Hayward
Model: VistaPool WiFi Module
Firmware version (from main.version)
Serial number (from wifi ID)

📦 Installation

Copy the folder hayward_vistapool into your Home Assistant config/ustom_components/ directory.
(Final path should be: config/custom_components/hayward_vistapool/)
Restart Home Assistant.

In Home Assistant, go to Settings → Devices & Services → Integrations → Add Integration.
Search for Hayward VistaPool.

⚙️ Configuration

During setup, you’ll need to provide:
Email (your VistaPool account)
Password (your VistaPool account password)
Pool ID (visible in the Firestore API document path, or in your VistaPool app data)

Options

Scan Interval – How often (in seconds) to poll VistaPool cloud for data. Default: 600 (10 minutes).
You can adjust this later in Integration Options in the UI.

📝 Notes

This integration is unofficial and not affiliated with Hayward.
It uses the Firebase + Firestore backend exposed by VistaPool / PoolWatch modules.
Data is read-only in the current version (control functions may be added in future).

Searise Developments specialises in custom software development and is an avid contributor to the HomeAssistant journey!