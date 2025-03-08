"""Petkit integration diagnostics."""

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

TO_REDACT = [CONF_PASSWORD, CONF_USERNAME]


async def async_get_device_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry, device: DeviceEntry
) -> dict[str, any]:
    """Return diagnostics for a config entry."""

    return {
        "config_entry": async_redact_data(config_entry.data, TO_REDACT),
    }
