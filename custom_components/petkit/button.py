"""Switch platform for Petkit Smart Devices integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from pypetkitapi.command import FeederCommand, LitterBoxCommand, LitterCommand
from pypetkitapi.const import D4H, D4S, D4SH, DEVICES_FEEDER, DEVICES_LITTER_BOX, D3
from pypetkitapi.feeder_container import Feeder
from pypetkitapi.litter_container import Litter
from pypetkitapi.water_fountain_container import WaterFountain

from .const import LOGGER
from .entity import PetKitDescSensorBase, PetkitEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import PetkitDataUpdateCoordinator
    from .data import PetkitConfigEntry


@dataclass(frozen=True, kw_only=True)
class PetKitButtonDesc(PetKitDescSensorBase, ButtonEntityDescription):
    """A class that describes sensor entities."""

    action: (
        Callable[[PetkitDataUpdateCoordinator, Feeder | Litter | WaterFountain], Any]
        | None
    ) = None


BUTTON_MAPPING: dict[type[Feeder | Litter | WaterFountain], list[PetKitButtonDesc]] = {
    Feeder: [
        PetKitButtonDesc(
            key="Reset desiccant",
            translation_key="reset_desiccant",
            action=lambda api, device: api.config_entry.runtime_data.client.send_api_request(
                device.id, FeederCommand.RESET_DESICCANT
            ),
            only_for_types=DEVICES_FEEDER,
        ),
        PetKitButtonDesc(
            key="Cancel manual feed",
            translation_key="cancel_manual_feed",
            action=lambda api, device: api.config_entry.runtime_data.client.send_api_request(
                device.id, FeederCommand.CANCEL_MANUAL_FEED
            ),
            only_for_types=DEVICES_FEEDER,
        ),
        PetKitButtonDesc(
            key="Call pet",
            translation_key="call_pet",
            action=lambda api, device: api.config_entry.runtime_data.client.send_api_request(
                device.id, FeederCommand.CALL_PET
            ),
            only_for_types=[D3],
        ),
        PetKitButtonDesc(
            key="Food replenished",
            translation_key="food_replenished",
            action=lambda api, device: api.config_entry.runtime_data.client.send_api_request(
                device.id, FeederCommand.FOOD_REPLENISHED
            ),
            only_for_types=[D4S, D4H, D4SH],
        ),
    ],
    Litter: [
        PetKitButtonDesc(
            key="Start cleaning",
            translation_key="start_cleaning",
            action=lambda api, device: api.config_entry.runtime_data.client.send_api_request(
                device.id, LitterCommand.CONTROL_DEVICE, LitterBoxCommand.START_CLEAN
            ),
            only_for_types=DEVICES_LITTER_BOX,
        ),
        PetKitButtonDesc(
            key="Pause cleaning",
            translation_key="pause_cleaning",
            action=lambda api, device: api.config_entry.runtime_data.client.send_api_request(
                device.id, LitterCommand.CONTROL_DEVICE, LitterBoxCommand.PAUSE_CLEAN
            ),
            only_for_types=DEVICES_LITTER_BOX,
        ),
    ],
    WaterFountain: [
        # TODO : Implementation is Client API
        # PetKitButtonDesc(
        #     key="Water filter reset",
        #     translation_key="water_filter_reset",
        #     action=lambda api, device: api.config_entry.runtime_data.client.send_api_request(
        #         device.id, WaterFountainCommand.RESET_FILTER
        #     ),
        #     only_for_types=[D4S, D4H, D4SH]
        # ),
    ],
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PetkitConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary_sensors using config entry."""
    devices = entry.runtime_data.client.device_list.values()
    entities = [
        PetkitButton(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
            device=device,
        )
        for device in devices
        for device_type, entity_descriptions in BUTTON_MAPPING.items()
        if isinstance(device, device_type)
        for entity_description in entity_descriptions
        if entity_description.is_supported(device)  # Check if the entity is supported
    ]
    async_add_entities(entities)


class PetkitButton(PetkitEntity, ButtonEntity):
    """Petkit Smart Devices Button class."""

    entity_description: PetKitButtonDesc

    def __init__(
        self,
        coordinator: PetkitDataUpdateCoordinator,
        entity_description: PetKitButtonDesc,
        device: Feeder | Litter | WaterFountain,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator, device)
        self.coordinator = coordinator
        self.entity_description = entity_description
        self.device = device

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the binary_sensor."""
        return (
            f"{self.device.device_type}_{self.device.sn}_{self.entity_description.key}"
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        LOGGER.debug("Button pressed: %s", self.entity_description.key)
        await self.entity_description.action(self.coordinator, self.device)
        await self.coordinator.async_request_refresh()
