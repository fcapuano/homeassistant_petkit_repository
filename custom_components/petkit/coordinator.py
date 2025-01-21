"""DataUpdateCoordinator for Petkit Smart Devices."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any

from pypetkitapi import (
    DownloadDecryptMedia,
    Feeder,
    Litter,
    MediaFile,
    MediaType,
    Pet,
    PetkitAuthenticationUnregisteredEmailError,
    PetkitRegionalServerNotFoundError,
    PetkitSessionError,
    PetkitSessionExpiredError,
    Purifier,
    PypetkitError,
    RecordType,
    WaterFountain,
)

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_MEDIA_DL_IMAGE,
    CONF_MEDIA_DL_VIDEO,
    CONF_MEDIA_EV_TYPE,
    DEFAULT_EVENTS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
)


class PetkitDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass, logger, name, update_interval, config_entry):
        """Initialize the data update coordinator."""
        super().__init__(hass, logger, name=name, update_interval=update_interval)
        self.config_entry = config_entry
        self.previous_devices = set()
        self.curent_devices = set()
        self.fast_poll_tic = 0

    async def _async_update_data(
        self,
    ) -> dict[int, Feeder | Litter | WaterFountain | Purifier | Pet]:
        """Update data via library."""

        if self.fast_poll_tic > 0:
            self.fast_poll_tic -= 1
            LOGGER.debug(f"Fast track tic remaining = {self.fast_poll_tic}")
        elif self.fast_poll_tic <= 0 and self.update_interval != timedelta(
            seconds=DEFAULT_SCAN_INTERVAL
        ):
            self.update_interval = timedelta(seconds=DEFAULT_SCAN_INTERVAL)
            LOGGER.debug("Fast track tic reset to default scan interval")

        try:
            await self.config_entry.runtime_data.client.get_devices_data()
        except (
            PetkitSessionExpiredError,
            PetkitSessionError,
            PetkitAuthenticationUnregisteredEmailError,
            PetkitRegionalServerNotFoundError,
        ) as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except PypetkitError as exception:
            raise UpdateFailed(exception) from exception
        else:
            data = self.config_entry.runtime_data.client.petkit_entities
            self.current_devices = set(data)

            # Check if there are any stale devices
            if stale_devices := self.previous_devices - self.current_devices:
                device_registry = dr.async_get(self.hass)
                for device_id in stale_devices:
                    device = device_registry.async_get(
                        identifiers={(DOMAIN, device_id)}
                    )
                    if device:
                        device_registry.async_update_device(
                            device_id=device.id,
                            remove_config_entry_id=self.config_entry.entry_id,
                        )
                self.previous_devices = self.current_devices
            return data


class PetkitMediaUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass, logger, name, update_interval, config_entry, data_coordinator
    ):
        """Initialize the data update coordinator."""
        super().__init__(hass, logger, name=name, update_interval=update_interval)
        self.config_entry = config_entry
        self.data_coordinator = data_coordinator
        self.media_type = []
        self.event_type = []
        self.previous_devices = set()
        self._get_media_config(config_entry.options)
        self.media_table = {}

    def _get_media_config(self, options) -> None:
        """Get media configuration."""
        event_type_config = options.get(CONF_MEDIA_EV_TYPE, DEFAULT_EVENTS)
        dl_image = options.get(CONF_MEDIA_DL_IMAGE, True)
        dl_video = options.get(CONF_MEDIA_DL_VIDEO, True)

        self.event_type = [RecordType(element.lower()) for element in event_type_config]

        if dl_image:
            self.media_type.append(MediaType.IMAGE)
        if dl_video:
            self.media_type.append(MediaType.VIDEO)

    async def _async_update_data(
        self,
    ) -> dict[str, list[MediaFile]]:
        """Update data via library."""

        self.hass.async_create_task(
            self._async_update_media_files(self.data_coordinator.current_devices)
        )
        return self.media_table

    async def _async_update_media_files(self, devices_lst: set) -> None:
        """Update media files."""
        client = self.config_entry.runtime_data.client
        media_path = Path(__file__).parent / "media"

        for device in devices_lst:
            if not hasattr(client.petkit_entities[device], "medias"):
                LOGGER.debug(f"Device id = {device} does not support medias")
                continue

            media_lst = client.petkit_entities[device].medias

            if not media_lst:
                LOGGER.debug(f"No medias found for device id = {device}")
                continue

            LOGGER.debug(f"Gathering medias files onto disk for device id = {device}")
            await client.media_manager.gather_all_media_from_disk(media_path, device)
            to_dl = await client.media_manager.list_missing_files(
                media_lst, self.media_type, self.event_type
            )

            dl_mgt = DownloadDecryptMedia(media_path, client)
            for media in to_dl:
                await dl_mgt.download_file(media, self.media_type)
            LOGGER.debug(
                f"Downloaded all medias for device id = {device} is OK (got {len(to_dl)} files to download)"
            )
            self.media_table[device] = (
                await client.media_manager.gather_all_media_from_disk(
                    media_path, device
                )
            )

        LOGGER.debug("Update media files finished for all devices")


class PetkitBluetoothUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass, logger, name, update_interval, config_entry, data_coordinator
    ):
        """Initialize the data update coordinator."""
        super().__init__(hass, logger, name=name, update_interval=update_interval)
        self.config_entry = config_entry
        self.data_coordinator = data_coordinator

    async def _async_update_data(
        self,
    ) -> dict[str, Any]:
        """Update data via library."""

        return {"test": "test"}
