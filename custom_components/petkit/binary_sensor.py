"""Binary sensor platform for Petkit Smart Devices integration."""

from __future__ import annotations


from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from pypetkitapi.const import D4SH, D4H, CTW3
from pypetkitapi.feeder_container import Feeder
from pypetkitapi.litter_container import Litter
from pypetkitapi.water_fountain_container import WaterFountain

from .entity import PetkitEntity, PetKitDescSensorBase

from .const import LOGGER


if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import PetkitDataUpdateCoordinator
    from .data import PetkitConfigEntry


@dataclass
class PetKitBinarySensorDesc(PetKitDescSensorBase, BinarySensorEntityDescription):
    """A class that describes sensor entities."""

    pass


BINARY_SENSOR_MAPPING: dict[
    type[Feeder | Litter | WaterFountain], list[PetKitBinarySensorDesc]
] = {
    Feeder: [
        PetKitBinarySensorDesc(
            key="camera_status",
            icon=lambda device: (
                "mdi:cctv" if device.state.camera_status else "mdi:cctv-off"
            ),
            value=lambda device: device.state.camera_status,
        ),
        PetKitBinarySensorDesc(
            key="feeding",
            icon=lambda device: "mdi:food-drumstick",
            device_class=BinarySensorDeviceClass.RUNNING,
            value=lambda device: device.state.feeding,
        ),
        PetKitBinarySensorDesc(
            key="battery_power",
            icon=lambda device: (
                "mdi:battery" if device.state.battery_power else "mdi:battery-off"
            ),
            value=lambda device: device.state.battery_power,
        ),
        PetKitBinarySensorDesc(
            key="care_plus_subscription",
            icon=lambda device: (
                "mdi:check-circle" if device.cloud_product.subscribe else "mdi:cancel"
            ),
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: device.cloud_product.subscribe,
        ),
        PetKitBinarySensorDesc(
            key="eating",
            icon=lambda device: "mdi:cat",
            device_class=BinarySensorDeviceClass.OCCUPANCY,
            value=lambda device: device.state.eating,
        ),
        PetKitBinarySensorDesc(
            key="food_level_1",
            icon=lambda device: (
                "mdi:food-drumstick-off"
                if device.state.food1 < 1
                else "mdi:food-drumstick"
            ),
            device_class=BinarySensorDeviceClass.PROBLEM,
            value=lambda device: device.state.food1 < 1,
        ),
        PetKitBinarySensorDesc(
            key="food_level_2",
            icon=lambda device: (
                "mdi:food-drumstick-off"
                if device.state.food2 < 1
                else "mdi:food-drumstick"
            ),
            device_class=BinarySensorDeviceClass.PROBLEM,
            value=lambda device: device.state.food2 < 1,
        ),
    ],
    Litter: [
        PetKitBinarySensorDesc(
            key="camera_status",
            icon=lambda device: (
                "mdi:cctv" if device.state.camera_status else "mdi:cctv-off"
            ),
            value=lambda device: device.state.camera,
            only_for_types=[D4H, D4SH],
        ),
        PetKitBinarySensorDesc(
            key="care_plus_subscription",
            icon=lambda device: (
                "mdi:check-circle" if device.cloud_product.subscribe else "mdi:cancel"
            ),
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: device.cloud_product.subscribe,
        ),
        PetKitBinarySensorDesc(
            key="liquid_empty",
            icon=lambda device: (
                "mdi:water-remove" if device.state.liquid_empty else "mdi:water-check"
            ),
            device_class=BinarySensorDeviceClass.PROBLEM,
            value=lambda device: device.state.liquid_empty,
        ),
        PetKitBinarySensorDesc(
            key="liquid_lack",
            icon=lambda device: (
                "mdi:water-alert" if device.state.liquid_lack else "mdi:water-check"
            ),
            device_class=BinarySensorDeviceClass.PROBLEM,
            value=lambda device: device.state.liquid_lack,
        ),
        PetKitBinarySensorDesc(
            key="sand_lack",
            icon=lambda device: (
                "mdi:wave-arrow-down" if device.state.sand_lack else "mdi:check-circle"
            ),
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
            icon=lambda device: (
                "mdi:delete-empty" if device.state.box_full else "mdi:delete"
            ),
            device_class=BinarySensorDeviceClass.PROBLEM,
            value=lambda device: device.state.box_full,
        ),
        PetKitBinarySensorDesc(
            key="waste_bin_presence",
            icon=lambda device: (
                "mdi:delete" if device.state.box_state else "mdi:delete-forever"
            ),
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
    """Set up binaery_sensors using config entry."""
    devices = (
        entry.runtime_data.client.device_list
    )  # Assuming devices are stored in runtime_data
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

    def __init__(
        self,
        coordinator: PetkitDataUpdateCoordinator,
        entity_description: PetKitBinarySensorDesc,
        device: Feeder | Litter | WaterFountain,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, device)
        self.entity_description = entity_description
        self._device = device

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        if self.entity_description.value:
            return self.entity_description.value(self._device)
        return None

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the binary_sensor."""
        return f"{self._device.id}_{self.entity_description.key}"

    @property
    def icon(self) -> str:
        """Return the icon based on the status."""
        return self.entity_description.icon(self._device)
