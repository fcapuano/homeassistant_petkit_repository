"""BlueprintEntity class."""

from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar

from pypetkitapi.feeder_container import Feeder
from pypetkitapi.litter_container import Litter
from pypetkitapi.water_fountain_container import WaterFountain

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, LOGGER
from .coordinator import PetkitDataUpdateCoordinator

_DevicesT = TypeVar("_DevicesT", bound=Feeder | Litter | WaterFountain)


class PetKitDescSensorBase(EntityDescription):
    """A class that describes sensor entities."""

    value: Callable[[Feeder | Litter | WaterFountain], Any] = None
    ignore_types: list[str] | None = None  # List of device types to ignore
    only_for_types: list[str] | None = (
        None  # Optional device types to filter the sensors
    )

    def __post_init__(self):
        """Post init."""
        if self.translation_key is None:
            self.translation_key = self.key

    def is_supported(self, device: Feeder | Litter | WaterFountain) -> bool:
        """Check if the entity is supported by trying to execute the value lambda."""

        if self.ignore_types:
            for ignore_device in self.ignore_types:
                if device.device_type.lower() == ignore_device:
                    LOGGER.debug(f"{device.device_type} force ignore for {self.key}")
                    return False

        if self.only_for_types:
            if device.device_type.lower() not in self.only_for_types:
                LOGGER.debug(f"{device.device_type} is NOT COMPATIBLE with {self.key}")
                return False

        if self.value is not None:
            try:
                self.value(device)
                LOGGER.debug(f"{device.device_type} support {self.key}")
            except AttributeError:
                LOGGER.debug(f"{device.device_type} DOES NOT support {self.key}")
                return False
        return True


class PetkitEntity(CoordinatorEntity[PetkitDataUpdateCoordinator], Generic[_DevicesT]):
    """BlueprintEntity class."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self, coordinator: PetkitDataUpdateCoordinator, device: _DevicesT
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.device = device
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device information for a Litter-Robot."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.device.sn)},
            manufacturer="Petkit",
            model=self.device.device_type,
            name=self.device.name,
            sw_version=self.device.firmware,
        )
