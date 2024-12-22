"""Custom integration to integrate Petkit Smart Devices with Home Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pypetkitapi.client import PetKitClient

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .const import COUNTRY_CODES, REGION, TIMEZONE
from .coordinator import PetkitDataUpdateCoordinator
from .data import PetkitData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import PetkitConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.TEXT,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.IMAGE,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PetkitConfigEntry,
) -> bool:
    """Set up this integration using UI."""

    country_from_ha = COUNTRY_CODES.get(
        hass.config.country if hass.config.country is not None else "Unknown"
    )
    tz_from_ha = hass.config.time_zone

    coordinator = PetkitDataUpdateCoordinator(
        hass=hass,
    )
    entry.runtime_data = PetkitData(
        client=PetKitClient(
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            region=entry.data.get(REGION, country_from_ha),
            timezone=entry.data.get(TIMEZONE, tz_from_ha),
            session=async_get_clientsession(hass),
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: PetkitConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: PetkitConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_update_options(hass: HomeAssistant, entry: PetkitConfigEntry) -> None:
    """Update options."""

    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: PetkitConfigEntry, device_entry: dr.DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    return True
