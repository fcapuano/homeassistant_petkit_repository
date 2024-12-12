"""Constants for Petkit Smart Devices integration."""

from logging import Logger, getLogger


LOGGER: Logger = getLogger(__package__)

DOMAIN = "petkit"
# TODO : What is the purpose of this ATTRIBUTION constant?
ATTRIBUTION = "Data provided by http://api.petkt.com"

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
