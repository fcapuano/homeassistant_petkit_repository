"""Switch platform for Petkit Smart Devices integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from pypetkitapi.command import FeederCommand, LitterBoxCommand, LitterCommand
from pypetkitapi.const import D4H, D4S, D4SH, DEVICES_FEEDER
from pypetkitapi.feeder_container import Feeder
from pypetkitapi.litter_container import Litter
from pypetkitapi.water_fountain_container import WaterFountain

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription

from .const import LOGGER
from .entity import PetKitDescSensorBase, PetkitEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import PetkitDataUpdateCoordinator
    from .data import PetkitConfigEntry


class PetKitButtonDesc(PetKitDescSensorBase, ButtonEntityDescription):
    """A class that describes sensor entities."""

    action: Callable[
        [PetkitDataUpdateCoordinator, Feeder | Litter | WaterFountain], Any
    ]


TEXT_MAPPING: dict[type[Feeder | Litter | WaterFountain], list[PetKitButtonDesc]] = {
    Feeder: [
        PetKitButtonDesc(
            key="reset_desiccant",
            action=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, FeederCommand.RESET_DESICCANT
            ),
            only_for_types=DEVICES_FEEDER,
        ),
        PetKitButtonDesc(
            key="cancel_manual_feed",
            action=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, FeederCommand.CANCEL_MANUAL_FEED
            ),
            only_for_types=DEVICES_FEEDER,
        ),
        PetKitButtonDesc(
            key="call_pet",
            action=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, FeederCommand.CALL_PET
            ),
            only_for_types=DEVICES_FEEDER,
        ),
        PetKitButtonDesc(
            key="food_repelenished",
            action=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, FeederCommand.FOOD_REPLENISHED
            ),
            only_for_types=[D4S, D4H, D4SH],
        ),
    ],
    Litter: [
        PetKitButtonDesc(
            key="start_cleaning",
            action=lambda api,
            device: api.config_entry.runtime_data.client.control_litter_box(
                device,
                LitterCommand.CONTROL_DEVICE,
            ),
            only_for_types=[Litter],
        ),
        PetKitButtonDesc(
            key="pause_cleaning",
            action=lambda api,
            device: api.config_entry.runtime_data.client.control_litter_box(
                device, LitterBoxCommand.PAUSE_CLEAN
            ),
            only_for_types=[Litter],
        ),
    ],
    WaterFountain: [
        # TODO : Implementation is Client API
        # PetKitButtonDesc(
        #     key="water_filter_reset",
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
        PetkitSwitch(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
            device=device,
        )
        for device in devices
        for device_type, entity_descriptions in TEXT_MAPPING.items()
        if isinstance(device, device_type)
        for entity_description in entity_descriptions
        if entity_description.is_supported(device)  # Check if the entity is supported
    ]
    async_add_entities(entities)


class PetkitSwitch(PetkitEntity, ButtonEntity):
    """Petkit Smart Devices Switch class."""

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
