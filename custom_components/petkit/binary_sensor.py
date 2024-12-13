"""Binary sensor platform for Petkit Smart Devices integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pypetkitapi.feeder_container import Feeder
from pypetkitapi.litter_container import Litter
from pypetkitapi.water_fountain_container import WaterFountain

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory

from .entity import PetKitDescSensorBase, PetkitEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import PetkitDataUpdateCoordinator
    from .data import PetkitConfigEntry


class PetKitBinarySensorDesc(PetKitDescSensorBase, BinarySensorEntityDescription):
    """A class that describes sensor entities."""


BINARY_SENSOR_MAPPING: dict[
    type[Feeder | Litter | WaterFountain], list[PetKitBinarySensorDesc]
] = {
    Feeder: [
        PetKitBinarySensorDesc(
            key="camera_status",
            value=lambda device: device.state.camera_status,
        ),
        PetKitBinarySensorDesc(
            key="feeding",
            device_class=BinarySensorDeviceClass.RUNNING,
            value=lambda device: device.state.feeding,
        ),
        PetKitBinarySensorDesc(
            key="battery_power",
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: device.state.battery_power,
        ),
        PetKitBinarySensorDesc(
            key="care_plus_subscription",
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: device.cloud_product.subscribe,
        ),
        PetKitBinarySensorDesc(
            key="eating",
            device_class=BinarySensorDeviceClass.OCCUPANCY,
            value=lambda device: device.state.eating,
        ),
        PetKitBinarySensorDesc(
            key="food_level_1",
            device_class=BinarySensorDeviceClass.PROBLEM,
            value=lambda device: device.state.food1 < 1,
        ),
        PetKitBinarySensorDesc(
            key="food_level_2",
            device_class=BinarySensorDeviceClass.PROBLEM,
            value=lambda device: device.state.food2 < 1,
        ),
    ],
    Litter: [
        PetKitBinarySensorDesc(
            key="camera_status",
            value=lambda device: device.state.camera,
        ),
        PetKitBinarySensorDesc(
            key="care_plus_subscription",
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: device.cloud_product.subscribe,
        ),
        PetKitBinarySensorDesc(
            key="liquid_empty",
            device_class=BinarySensorDeviceClass.PROBLEM,
            value=lambda device: device.state.liquid_empty,
        ),
        PetKitBinarySensorDesc(
            key="liquid_lack",
            device_class=BinarySensorDeviceClass.PROBLEM,
            value=lambda device: device.state.liquid_lack,
        ),
        PetKitBinarySensorDesc(
            key="sand_lack",
            device_class=BinarySensorDeviceClass.PROBLEM,
            value=lambda device: device.state.sand_lack,
        ),
        # TODO : Add disabled by default
        PetKitBinarySensorDesc(
            key="low_power",
            value=lambda device: device.state.low_power,
        ),
        PetKitBinarySensorDesc(
            key="power",
            device_class=BinarySensorDeviceClass.POWER,
            value=lambda device: device.state.power,
        ),
        PetKitBinarySensorDesc(
            key="waste_bin",
            device_class=BinarySensorDeviceClass.PROBLEM,
            value=lambda device: device.state.box_full,
        ),
        PetKitBinarySensorDesc(
            key="waste_bin_presence",
            device_class=BinarySensorDeviceClass.PROBLEM,
            value=lambda device: not device.state.box_state,
        ),
    ],
    WaterFountain: [
        PetKitBinarySensorDesc(
            key="no_disturbing_switch",
            name="no_disturbing_switch",
            value=lambda device: device.settings.no_disturbing_switch,
        ),
        PetKitBinarySensorDesc(
            key="lack_warning",
            name="lack_warning",
            value=lambda device: device.lack_warning,
        ),
        PetKitBinarySensorDesc(
            key="low_battery",
            name="low_battery",
            value=lambda device: device.lack_warning,
        ),
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
        PetkitBinarySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
            device=device,
        )
        for device in devices
        for device_type, entity_descriptions in BINARY_SENSOR_MAPPING.items()
        if isinstance(device, device_type)
        for entity_description in entity_descriptions
        if entity_description.is_supported(device)  # Check if the entity is supported
    ]
    async_add_entities(entities)


class PetkitBinarySensor(PetkitEntity, BinarySensorEntity):
    """Petkit Smart Devices BinarySensor class."""

    entity_description: PetKitBinarySensorDesc

    def __init__(
        self,
        coordinator: PetkitDataUpdateCoordinator,
        entity_description: PetKitBinarySensorDesc,
        device: Feeder | Litter | WaterFountain,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, device)
        self.entity_description = entity_description
        self.device = device

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the binary_sensor."""
        return f"{self.device.id}_{self.entity_description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if (
            updated_device := self.coordinator.data.get(str(self.device.id))
        ) and self.entity_description.value:
            return bool(self.entity_description.value(updated_device))
        return None
