"""Switch platform for Petkit Smart Devices integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.select import SelectEntityDescription, SelectEntity
from pypetkitapi.command import FeederCommand, DeviceCommand
from pypetkitapi.const import D3, D4, D4H, D4S, D4SH, FEEDER, FEEDER_MINI
from pypetkitapi.feeder_container import Feeder
from pypetkitapi.litter_container import Litter
from pypetkitapi.water_fountain_container import WaterFountain

from .const import LOGGER, SURPLUS_FOOD_LEVEL_OPT
from .entity import PetKitDescSensorBase, PetkitEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import PetkitDataUpdateCoordinator
    from .data import PetkitConfigEntry


@dataclass(frozen=True, kw_only=True)
class PetKitSelectDesc(PetKitDescSensorBase, SelectEntityDescription):
    """A class that describes sensor entities."""

    current_option: Callable[[Feeder | Litter | WaterFountain], str] | None = None
    options: Callable[[], list[str]] | None = None
    action: (
        Callable[[PetkitConfigEntry, Feeder | Litter | WaterFountain, str], Any] | None
    ) = None


SELECT_MAPPING: dict[type[Feeder | Litter | WaterFountain], list[PetKitSelectDesc]] = {
    Feeder: [
        PetKitSelectDesc(
            key="Surplus level",
            translation_key="surplus_level",
            current_option=lambda device: SURPLUS_FOOD_LEVEL_OPT[
                device.settings.surplus_standard
            ],
            options=lambda: list(SURPLUS_FOOD_LEVEL_OPT.values()),
            action=lambda api, device, opt_value: api.config_entry.runtime_data.client.send_api_request(
                device.id,
                DeviceCommand.UPDATE_SETTING,
                {
                    "surplusStandard": next(
                        key
                        for key, value in SURPLUS_FOOD_LEVEL_OPT.items()
                        if value == opt_value
                    )
                },
            ),
            only_for_types=[D4H, D4SH],
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
    """Set up binary_sensors using config entry."""
    devices = entry.runtime_data.client.device_list.values()
    entities = [
        PetkitSelect(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
            device=device,
        )
        for device in devices
        for device_type, entity_descriptions in SELECT_MAPPING.items()
        if isinstance(device, device_type)
        for entity_description in entity_descriptions
        if entity_description.is_supported(device)  # Check if the entity is supported
    ]
    async_add_entities(entities)


class PetkitSelect(PetkitEntity, SelectEntity):
    """Petkit Smart Devices Select class."""

    entity_description: PetKitSelectDesc

    def __init__(
        self,
        coordinator: PetkitDataUpdateCoordinator,
        entity_description: PetKitSelectDesc,
        device: Feeder | Litter | WaterFountain,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator, device)
        self.coordinator = coordinator
        self.entity_description = entity_description
        self.device = device

    @property
    def current_option(self) -> str:
        """Return the current surplus food level option."""
        return self.entity_description.current_option(self.device)

    @property
    def options(self) -> list[str]:
        """Return list of all available manual feed amounts."""
        return self.entity_description.options()

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the binary_sensor."""
        return (
            f"{self.device.device_type}_{self.device.sn}_{self.entity_description.key}"
        )

    async def async_select_option(self, value: str) -> None:
        """Set manual feeding amount."""
        LOGGER.debug(
            "Setting value for : %s with value : %s", self.entity_description.key, value
        )
        await self.entity_description.action(self.coordinator, self.device, value)
