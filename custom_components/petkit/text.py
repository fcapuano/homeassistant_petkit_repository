"""Switch platform for Petkit Smart Devices integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.text import TextEntity, TextEntityDescription
from homeassistant.const import EntityCategory
from pypetkitapi.command import FeederCommand
from pypetkitapi.const import D3, D4, D4H, D4S, D4SH, FEEDER, FEEDER_MINI
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
class PetKitTextDesc(PetKitDescSensorBase, TextEntityDescription):
    """A class that describes sensor entities."""

    native_value: str | None = None
    action: (
        Callable[[PetkitConfigEntry, Feeder | Litter | WaterFountain, str], Any] | None
    ) = None


TEXT_MAPPING: dict[type[Feeder | Litter | WaterFountain], list[PetKitTextDesc]] = {
    Feeder: [
        PetKitTextDesc(
            key="Manual feed single",
            translation_key="manual_feed_single",
            value=lambda device: device.settings.light_mode,
            entity_category=EntityCategory.CONFIG,
            native_min=3,
            native_max=5,
            pattern="^([0-9]|10)$",
            native_value="0",
            action=lambda api, device, amount_value: api.config_entry.runtime_data.client.send_api_request(
                device.id, FeederCommand.MANUAL_FEED, {"amount": int(amount_value)}
            ),
            only_for_types=[FEEDER, FEEDER_MINI, D3, D4, D4H],
        ),
        PetKitTextDesc(
            key="Manual feed dual h1",
            translation_key="manual_feed_dual_h1",
            value=lambda device: device.settings.light_mode,
            native_min=1,
            native_max=2,
            pattern="^([0-9]|10)$",
            native_value="0",
            action=lambda api, device, amount_value: api.config_entry.runtime_data.client.send_api_request(
                device.id,
                FeederCommand.MANUAL_FEED_DUAL,
                {"amount1": int(amount_value), "amount2": 0},
            ),
            only_for_types=[D4S, D4SH],
        ),
        PetKitTextDesc(
            key="Manual feed dual h2",
            translation_key="manual_feed_dual_h2",
            value=lambda device: device.settings.light_mode,
            native_min=1,
            native_max=2,
            pattern="^([0-9]|10)$",
            native_value="0",
            action=lambda api, device, amount_value: api.config_entry.runtime_data.client.send_api_request(
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
    devices = entry.runtime_data.client.device_list.values()
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

    entity_description: PetKitTextDesc

    def __init__(
        self,
        coordinator: PetkitDataUpdateCoordinator,
        entity_description: PetKitTextDesc,
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

    async def async_set_value(self, value: str) -> None:
        """Set manual feeding amount."""
        LOGGER.debug(
            "Setting value for : %s with value : %s", self.entity_description.key, value
        )
        await self.entity_description.action(self.coordinator, self.device, value)
