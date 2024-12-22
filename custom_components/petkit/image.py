"""Image platform for Petkit Smart Devices integration."""

from __future__ import annotations

from dataclasses import dataclass
import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import aiofiles
from pypetkitapi.const import D4H, D4SH
from pypetkitapi.containers import Pet
from pypetkitapi.feeder_container import Feeder
from pypetkitapi.litter_container import Litter
from pypetkitapi.medias import MediaHandler
from pypetkitapi.water_fountain_container import WaterFountain

from homeassistant.components.image import ImageEntity, ImageEntityDescription

from .const import LOGGER
from .entity import PetKitDescSensorBase, PetkitEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import PetkitDataUpdateCoordinator
    from .data import PetkitConfigEntry


@dataclass(frozen=True, kw_only=True)
class PetKitImageDesc(PetKitDescSensorBase, ImageEntityDescription):
    """A class that describes sensor entities."""

    event_key: str | None = None  # Event key to get the image from


IMAGE_MAPPING: dict[type[Feeder | Litter | WaterFountain], list[PetKitImageDesc]] = {
    Feeder: [
        PetKitImageDesc(
            key="Last visit event",
            event_key="pet",
            translation_key="last_visit_event",
            only_for_types=[D4SH, D4H],
        ),
        PetKitImageDesc(
            key="Last eat event",
            event_key="eat",
            translation_key="last_eat_event",
            only_for_types=[D4SH, D4H],
        ),
        PetKitImageDesc(
            key="Last feed event",
            event_key="feed",
            translation_key="last_feed_event",
            only_for_types=[D4SH, D4H],
        ),
    ],
    Litter: [],
    WaterFountain: [],
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PetkitConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary_sensors using config entry."""
    devices = entry.runtime_data.client.petkit_entities.values()
    entities = [
        PetkitImage(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
            device=device,
        )
        for device in devices
        for device_type, entity_descriptions in IMAGE_MAPPING.items()
        if isinstance(device, device_type)
        for entity_description in entity_descriptions
        if entity_description.is_supported(device)
    ]
    async_add_entities(entities)


class PetkitImage(PetkitEntity, ImageEntity):
    """Petkit Smart Devices Image class."""

    entity_description: PetKitImageDesc

    def __init__(
        self,
        coordinator: PetkitDataUpdateCoordinator,
        entity_description: PetKitImageDesc,
        device: Feeder | Litter | WaterFountain | Pet,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator, device)
        ImageEntity.__init__(self, coordinator.hass)
        self.coordinator = coordinator
        self.entity_description = entity_description
        self.device = device
        self.media_handler = MediaHandler(Path(__file__).parent / "images")
        self._last_image_timestamp: datetime.datetime | None = None
        self._last_image_filename: str | None = None

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the binary_sensor."""
        return (
            f"{self.device.device_type}_{self.device.sn}_{self.entity_description.key}"
        )

    @property
    def image_last_updated(self) -> datetime.datetime | None:
        """Return timestamp of last image update."""
        return self._last_image_timestamp

    async def async_image(self) -> bytes | None:
        """Return bytes of image asynchronously."""
        event_key = self.entity_description.event_key

        await self.media_handler.get_last_image(
            self.coordinator.data.get(self.device.id)
        )
        await self._get_filename_and_timestamp_for_event_key(
            self.media_handler.media_files, event_key
        )

        if self._last_image_filename:
            try:
                image_path = (
                    Path(__file__).parent / "images" / self._last_image_filename
                )
                LOGGER.debug(
                    f"Getting image for {self.device.device_type} Path is :{image_path}"
                )
                async with aiofiles.open(image_path, "rb") as image_file:
                    return await image_file.read()
            except FileNotFoundError:
                LOGGER.error("Image file not found")
                return None
        else:
            LOGGER.error(f"No filename found for event key '{event_key}'")
            return None

    async def _get_filename_and_timestamp_for_event_key(self, media_files, event_key):
        """Parse media files and return the filename and timestamp for the given event key."""
        for media_file in media_files:
            if media_file.record_type == event_key:
                timestamp = datetime.datetime.fromtimestamp(media_file.timestamp)
                self._last_image_timestamp = timestamp
                self._last_image_filename = media_file.filename
