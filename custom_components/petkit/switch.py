"""Switch platform for Petkit Smart Devices integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import EntityCategory
from pypetkitapi.command import DeviceCommand
from pypetkitapi.feeder_container import Feeder
from pypetkitapi.litter_container import Litter
from pypetkitapi.water_fountain_container import WaterFountain

from .const import LOGGER
from .entity import PetkitEntity, PetKitDescSensorBase

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import PetkitDataUpdateCoordinator
    from .data import PetkitConfigEntry


@dataclass
class PetKitSwitchDesc(PetKitDescSensorBase, SwitchEntityDescription):
    """A class that describes sensor entities."""

    turn_on: Callable[[Feeder | Litter | WaterFountain], Any] | None = None
    turn_off: Callable[[Feeder | Litter | WaterFountain], Any] | None = None


SWITCH_MAPPING: dict[type[Feeder | Litter | WaterFountain], list[PetKitSwitchDesc]] = {
    Feeder: [
        PetKitSwitchDesc(
            key="indicator_light",
            icon=lambda device: (
                "mdi:lightbulb"
                if device.settings.light_mode == 1
                else "mdi:lightbulb-off"
            ),
            value=lambda device: device.settings.light_mode,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api, device: api.config_entry.runtime_data.client.send_api_request(
                device, DeviceCommand.UPDATE_SETTING, {"lightMode": 1}
            ),
            turn_off=lambda api, device: api.config_entry.runtime_data.client.send_api_request(
                device, DeviceCommand.UPDATE_SETTING, {"lightMode": 0}
            ),
        )
    ],
    Litter: [],
    WaterFountain: [],
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PetkitConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors using config entry."""
    devices = (
        entry.runtime_data.client.device_list
    )  # Assuming devices are stored in runtime_data
    entities = [
        PetkitSwitch(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
            device=device,
        )
        for device in devices
        for device_type, entity_descriptions in SWITCH_MAPPING.items()
        if isinstance(device, device_type)
        for entity_description in entity_descriptions
        if entity_description.is_supported(device)  # Check if the entity is supported
    ]
    async_add_entities(entities)


class PetkitSwitch(PetkitEntity, SwitchEntity):
    """Petkit Smart Devices Switch class."""

    def __init__(
        self,
        coordinator: PetkitDataUpdateCoordinator,
        entity_description: PetKitSwitchDesc,
        device: Feeder | Litter | WaterFountain,

    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator, device)
        self.coordinator = coordinator
        self.entity_description = entity_description
        self._device = device

    @property
    def icon(self) -> str:
        """Return the icon for the switch."""
        return self.entity_description.icon(self._device)

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return bool(self.entity_description.value(self._device))

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the switch."""
        LOGGER.debug(f"Turn ON")
        # TODO : To fix not working
        await self.entity_description.turn_on(self.coordinator, self._device)

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the switch."""
        LOGGER.debug(f"Turn OFF")
        await self.entity_description.turn_off(self.coordinator, self._device)
