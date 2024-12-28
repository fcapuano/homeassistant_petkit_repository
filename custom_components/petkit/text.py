"""Switch platform for Petkit Smart Devices integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pypetkitapi.command import FeederCommand
from pypetkitapi.const import D3, D4, D4H, D4S, D4SH, FEEDER, FEEDER_MINI
from pypetkitapi.feeder_container import Feeder
from pypetkitapi.litter_container import Litter
from pypetkitapi.water_fountain_container import WaterFountain

from homeassistant.components.text import TextEntity, TextEntityDescription

from .const import INPUT_FEED_PATTERN, LOGGER, ONLINE_STATE
from .entity import PetKitDescSensorBase, PetkitEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import PetkitDataUpdateCoordinator
    from .data import PetkitConfigEntry, PetkitDevices


@dataclass(frozen=True, kw_only=True)
class PetkitTextDesc(PetKitDescSensorBase, TextEntityDescription):
    """A class that describes sensor entities."""

    native_value: str | None = None
    action: Callable[[PetkitConfigEntry, PetkitDevices, str], Any] | None = None


TEXT_MAPPING: dict[type[PetkitDevices], list[PetkitTextDesc]] = {
    Feeder: [
        PetkitTextDesc(
            key="Manual feed single",
            translation_key="manual_feed_single",
            value=lambda device: device.settings.light_mode,
            native_min=1,
            native_max=2,
            pattern=INPUT_FEED_PATTERN,
            native_value="0",
            action=lambda api, device, amount_value: api.send_api_request(
                device.id, FeederCommand.MANUAL_FEED, {"amount": int(amount_value)}
            ),
            only_for_types=[FEEDER, FEEDER_MINI, D3, D4, D4H],
        ),
        PetkitTextDesc(
            key="Manual feed dual h1",
            translation_key="manual_feed_dual_h1",
            value=lambda device: device.settings.light_mode,
            native_min=1,
            native_max=2,
            pattern=INPUT_FEED_PATTERN,
            native_value="0",
            action=lambda api, device, amount_value: api.send_api_request(
                device.id,
                FeederCommand.MANUAL_FEED_DUAL,
                {"amount1": int(amount_value), "amount2": 0},
            ),
            only_for_types=[D4S, D4SH],
        ),
        PetkitTextDesc(
            key="Manual feed dual h2",
            translation_key="manual_feed_dual_h2",
            value=lambda device: device.settings.light_mode,
            native_min=1,
            native_max=2,
            pattern=INPUT_FEED_PATTERN,
            native_value="0",
            action=lambda api, device, amount_value: api.send_api_request(
                device.id,
                FeederCommand.MANUAL_FEED_DUAL,
                {"amount1": 0, "amount2": int(amount_value)},
            ),
            only_for_types=[D4S, D4SH],
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
        PetkitText(
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


class PetkitText(PetkitEntity, TextEntity):
    """Petkit Smart Devices Switch class."""

    entity_description: PetkitTextDesc

    def __init__(
        self,
        coordinator: PetkitDataUpdateCoordinator,
        entity_description: PetkitTextDesc,
        device: PetkitDevices,
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

    @property
    def native_max(self) -> int:
        """Max number of characters."""

        return self.entity_description.native_max

    @property
    def native_min(self) -> int:
        """Min number of characters."""

        return self.entity_description.native_min

    @property
    def pattern(self) -> str | None:
        """Check validity with regex pattern."""

        return self.entity_description.pattern

    @property
    def native_value(self) -> str:
        """Always reset to native_value"""

        return self.entity_description.native_value

    @property
    def available(self) -> bool:
        """Return if this button is available or not"""
        device_data = self.coordinator.data.get(self.device.id)
        if hasattr(device_data.state, "pim"):
            return device_data.state.pim in ONLINE_STATE
        return True

    async def async_set_value(self, value: str) -> None:
        """Set manual feeding amount."""

        if self.device.device_type in [D4, D4H]:
            # D4/D4H => 10,20,30,40,50
            valid_values = [10, 20, 30, 40, 50]
        elif self.device.device_type == FEEDER_MINI:
            # FeederMini => 0,5,10,15,20,25,30,35,40,45,50
            valid_values = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
        elif self.device.device_type == D3:
            # D3 => 5 to 200
            valid_values = list(range(5, 201))
        else:
            # Other, D4sh => 1,2,3,4,5,7,8,9,10
            valid_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        if int(value) not in valid_values:
            raise ValueError(
                f"Feeding value '{value}' is not valid for this feeder. Valid values are: {valid_values}"
            )

        LOGGER.debug(
            "Setting value for : %s with value : %s", self.entity_description.key, value
        )
        await self.entity_description.action(
            self.coordinator.config_entry.runtime_data.client, self.device, value
        )
