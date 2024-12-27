"""Petkit integration diagnostics."""

from typing import TYPE_CHECKING

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant

from .data import PetkitConfigEntry, PetkitDevices

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


TO_REDACT = [
    CONF_PASSWORD,
]


def _get_appliance_by_device_id(
    hass: HomeAssistant, entry: PetkitConfigEntry, device_id: str
) -> PetkitDevices:
    """Retrieve the appliance data by device ID."""
    for device in entry.runtime_data.client.petkit_entities.values():
        if device.id == device_id:
            return device
    raise ValueError(f"Device with ID {device_id} not found")


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
):
    """Return config entry diagnostics."""
    return {
        "title": "Petkit config entry diagnostics",
        "type": "config_entry",
        "identifier": config_entry.entry_id,
        "config_data": config_entry.data,
        "config_options": config_entry.options,
    }


async def async_get_device_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
    device: PetkitDevices,
) -> dict[str, any]:
    """Return diagnostics for a device."""
    appliance = _get_appliance_by_device_id(hass, entry, device.id)
    return {
        "details": async_redact_data(appliance.raw_data, TO_REDACT),
        "data": appliance.data,
    }