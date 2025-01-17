"""DataUpdateCoordinator for Petkit Smart Devices."""

from __future__ import annotations

from pathlib import Path

from pypetkitapi import (
    DownloadDecryptMedia,
    Feeder,
    Litter,
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

from . import CONF_BLE_RELAY_ENABLED
from .const import (
    CONF_MEDIA_DL_IMAGE,
    CONF_MEDIA_DL_VIDEO,
    CONF_MEDIA_EV_TYPE,
    DEFAULT_EVENTS,
    DOMAIN,
    LOGGER,
)


class PetkitDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass, logger, name, update_interval, config_entry):
        """Initialize the data update coordinator."""
        super().__init__(hass, logger, name=name, update_interval=update_interval)
        self.config_entry = config_entry
        self.bluetooth_relay_enabled = config_entry.options.get(
            CONF_BLE_RELAY_ENABLED, True
        )
        self.media_table = []
        self.media_type = []
        self.event_type = []
        self.previous_devices = set()
        self._get_media_config(config_entry.options)

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
    ) -> dict[int, Feeder | Litter | WaterFountain | Purifier | Pet]:
        """Update data via library."""
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
            current_devices = set(data)

            # Run _async_update_media_files in the background
            self.hass.async_create_task(self._async_update_media_files(current_devices))

            # Check if there are any stale devices
            if stale_devices := self.previous_devices - current_devices:
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
                self.previous_devices = current_devices
            return data

    async def _async_update_media_files(self, devices_lst: set) -> None:
        """Update media files."""
        client = self.config_entry.runtime_data.client
        media_path = Path(__file__).parent / "media"

        self.media_table.clear()

        for device in devices_lst:
            if not hasattr(client.petkit_entities[device], "medias"):
                LOGGER.debug(f"Device id = {device} does not support medias")
                continue

            media_lst = client.petkit_entities[device].medias

            if not media_lst:
                LOGGER.debug(f"No medias found for device id = {device}")
                continue

            LOGGER.debug(f"Gathering medias files onto disk for device id = {device}")
            await client.media_manager.get_all_media_files_disk(media_path, device)
            to_dl = await client.media_manager.prepare_missing_files(
                media_lst, self.media_type, self.event_type
            )

            dl_mgt = DownloadDecryptMedia(media_path, client)
            for media in to_dl:
                LOGGER.debug(f"Downloading : {media}")
                await dl_mgt.download_file(media, self.media_type)
            LOGGER.debug(
                f"Downloaded all medias for device id = {device} is OK (got {len(to_dl)} files to download)"
            )
            await client.media_manager.get_all_media_files_disk(media_path, device)
            self.media_table.extend(client.media_manager.media_table)
        LOGGER.debug("Update media files finished for all devices")
