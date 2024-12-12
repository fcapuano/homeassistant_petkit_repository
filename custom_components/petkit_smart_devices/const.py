"""Constants for petkit_smart_devices."""

from logging import Logger, getLogger


LOGGER: Logger = getLogger(__package__)

DOMAIN = "petkit_smart_devices"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"

# Data mapping for petkit devices
DEVICE_STATUS_MAP = {
    0: "Offline",
    1: "Online",
    2: "On battery",
}

BATTERY_LEVEL_MAP = {
    0: "Low",
    1: "Normal",
}
