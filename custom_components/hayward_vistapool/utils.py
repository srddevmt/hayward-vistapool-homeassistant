from __future__ import annotations

import logging
import math
import re
from typing import Any, Dict, Tuple, Optional

_LOGGER = logging.getLogger(__name__)

FIRESTORE_VALUE_KEYS = (
    "integerValue",
    "doubleValue",
    "booleanValue",
    "stringValue",
    "mapValue",
    "arrayValue",
)

# Heuristic patterns for classification
BINARY_HINTS = re.compile(r"(?:^|\.|_)(is|has|enabled|present|onoff|pump_status|status|al\d+|fl\d+)(?:$|\b)", re.IGNORECASE)
TEMP_HINT = re.compile(r"(?:^|\.|_)(temp|temperature)(?:$|\b)", re.IGNORECASE)
RSSI_HINT = re.compile(r"(?:^|\.|_)(rssi|signal)(?:$|\b)", re.IGNORECASE)
ORP_HINT = re.compile(r"(?:^|\.|_)(orp|rx\.status\.value)(?:$|\b)", re.IGNORECASE)
PH_HINT = re.compile(r"(?:^|\.|_)(ph)(?:$|\b)", re.IGNORECASE)
LEVEL_HINT = re.compile(r"(?:^|\.|_)(level)(?:$|\b)", re.IGNORECASE)
TIME_HINT = re.compile(r"(?:^|\.|_)(time|remainingTime|startAt|interval|partial|total)(?:$|\b)", re.IGNORECASE)
FREQ_HINT = re.compile(r"(?:^|\.|_)(freq)(?:$|\b)", re.IGNORECASE)
PERCENT_HINT = re.compile(r"(?:^|\.|_)(tank|water_level|reduction|cover|to2|from2)(?:$|\b)", re.IGNORECASE)

def unwrap_firestore_value(value: Any) -> Any:
    """Recursively unwrap Firestore REST API typed values into Python primitives."""
    if not isinstance(value, dict):
        return value

    for key in FIRESTORE_VALUE_KEYS:
        if key in value:
            v = value[key]
            if key == "integerValue":
                try:
                    return int(v)
                except Exception:
                    return None
            if key == "doubleValue":
                try:
                    return float(v)
                except Exception:
                    return None
            if key == "booleanValue":
                return bool(v)
            if key == "stringValue":
                return str(v)
            if key == "mapValue":
                fields = v.get("fields", {})
                return {k: unwrap_firestore_value(subv) for k, subv in fields.items()}
            if key == "arrayValue":
                arr = v.get("values", [])
                return [unwrap_firestore_value(subv) for subv in arr]

    if "fields" in value:  # nested docs
        return {k: unwrap_firestore_value(subv) for k, subv in value["fields"].items()}
    return value


def unwrap_firestore_doc(doc_json: Dict[str, Any]) -> Dict[str, Any]:
    fields = doc_json.get("fields", {})
    clean = {k: unwrap_firestore_value(v) for k, v in fields.items()}
    _LOGGER.debug("Unwrapped Firestore doc with %d top-level keys", len(clean))
    return clean


def flatten_dict(data: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    items: Dict[str, Any] = {}
    for k, v in (data or {}).items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


def coerce_number(val: Any) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        f = float(val)
        if math.isnan(f):
            return None
        return f
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return None
        try:
            f = float(s)
            if math.isnan(f):
                return None
            return f
        except Exception:
            return None
    return None


def coerce_bool(val: Any) -> Optional[bool]:
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        if val in (0, 1):
            return bool(val)
        return None
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ("true", "on", "yes", "1"):
            return True
        if v in ("false", "off", "no", "0"):
            return False
    return None


def pretty_name_from_path(path: str) -> str:
    text = path.replace(".", " ").replace("_", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text.title()


def guess_unit_and_device_class(path: str, raw_val: Any) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Return (unit, device_class_name, state_class_name). Device class/state class are HA enum names."""
    unit = None
    device_class = None
    state_class = "measurement"  # default for numeric

    if TEMP_HINT.search(path):
        unit = "°C"
        device_class = "temperature"
        return unit, device_class, state_class

    if RSSI_HINT.search(path):
        unit = "dBm"
        device_class = "signal_strength"
        return unit, device_class, state_class

    if ORP_HINT.search(path):
        unit = "mV"
        device_class = None
        return unit, device_class, state_class

    if PH_HINT.search(path):
        # pH has no unit symbol; HA has a PH device class in newer builds
        unit = "pH"
        device_class = "ph"
        return unit, device_class, state_class

    if LEVEL_HINT.search(path) or PERCENT_HINT.search(path):
        num = coerce_number(raw_val)
        if num is not None and 0 <= num <= 100:
            unit = "%"
        return unit, device_class, state_class

    if TIME_HINT.search(path) or FREQ_HINT.search(path):
        unit = "s"
        return unit, device_class, state_class

    # Totals that likely increase
    if re.search(r"(?:^|\.|_)(total|cellTotalTime)(?:$|\b)", path, re.IGNORECASE):
        state_class = "total_increasing"

    return unit, device_class, state_class


def classify_field(path: str, value: Any) -> str:
    """Classify into 'binary', 'sensor', or 'text'."""
    b = coerce_bool(value)
    if b is not None:
        return "binary"

    # Numeric 0/1 with binary hint in path -> binary
    num = coerce_number(value)
    if num is not None and num in (0.0, 1.0) and BINARY_HINTS.search(path):
        return "binary"

    if num is not None:
        return "sensor"

    if isinstance(value, str):
        return "sensor"  # expose as text sensor

    # Fallback: ignore complex types
    return "ignore"


def transform_value_for_display(path: str, value: Any) -> Any:
    """Apply value transforms (e.g., pH x100 scaling)."""
    num = coerce_number(value)
    if num is None:
        return value

    # pH values often come as x100 (e.g., 700 -> 7.00)
    if PH_HINT.search(path) and num > 14:
        return round(num / 100.0, 2)

    return num