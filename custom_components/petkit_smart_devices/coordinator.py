"""DataUpdateCoordinator for petkit_smart_devices."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from pypetkitapi.exceptions import (
    PypetkitError,
)
from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import PetkitConfigEntry


class PetkitDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: PetkitConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.get_devices_data()
        except PypetkitError as exception:
            raise UpdateFailed(exception) from exception
        # TODO : Add more exception to catch
        # except PypetkitError as exception:
        #     raise ConfigEntryAuthFailed(exception) from exception
