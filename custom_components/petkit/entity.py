"""Petkit Smart Devices Entity class."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from pypetkitapi.containers import Pet
from pypetkitapi.feeder_container import Feeder
from pypetkitapi.litter_container import Litter
from pypetkitapi.water_fountain_container import WaterFountain

from homeassistant.helpers.device_registry import DeviceInfo, CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER, PETKIT_DEVICES_MAPPING
from .coordinator import PetkitDataUpdateCoordinator

_DevicesT = TypeVar("_DevicesT", bound=Feeder | Litter | WaterFountain | Pet)


@dataclass(frozen=True, kw_only=True)
class PetKitDescSensorBase(EntityDescription):
    """A class that describes sensor entities."""

    value: Callable[[_DevicesT], Any] | None = None
    ignore_types: list[str] | None = None  # List of device types to ignore
    only_for_types: list[str] | None = None  # List of device types to support
    force_add: list[str] | None = None

    def is_supported(self, device: _DevicesT) -> bool:
        """Check if the entity is supported by trying to execute the value lambda."""

        if not isinstance(device, (Feeder, Litter, WaterFountain | Pet)):
            LOGGER.error(
                f"Device instance is not of expected type: {type(device)} can't check support"
            )
            return False

        device_type = getattr(device, "device_type", None)
        if not device_type:
            LOGGER.error(f"Device {device.name} has no type, can't check support")
            return False

        if self._is_force_added(device_type):
            return True

        if self._is_ignored(device_type):
            return False

        if self._is_not_in_supported_types(device_type):
            return False

        return self._check_value_support(device)

    def _is_force_added(self, device_type: str) -> bool:
        """Check if the device is in the force_add list."""
        if self.force_add and device_type in self.force_add:
            LOGGER.debug(f"{device_type} force add for '{self.key}'")
            return True
        return False

    def _is_ignored(self, device_type: str) -> bool:
        """Check if the device is in the ignore_types list."""
        if self.ignore_types and device_type in self.ignore_types:
            LOGGER.debug(f"{device_type} force ignore for '{self.key}'")
            return True
        return False

    def _is_not_in_supported_types(self, device_type: str) -> bool:
        """Check if the device is not in the only_for_types list."""
        if self.only_for_types and device_type not in self.only_for_types:
            LOGGER.debug(f"{device_type} is NOT COMPATIBLE with '{self.key}'")
            return True
        return False

    def _check_value_support(self, device: _DevicesT) -> bool:
        """Check if the device supports the value lambda."""
        if self.value is not None:
            try:
                result = self.value(device)
                if result is None:
                    LOGGER.debug(
                        f"{device.device_type} DOES NOT support '{self.key}' (value is None)"
                    )
                    return False
                LOGGER.debug(f"{device.device_type} supports '{self.key}'")
            except AttributeError:
                LOGGER.debug(f"{device.device_type} DOES NOT support '{self.key}'")
                return False
        return True


class PetkitEntity(CoordinatorEntity[PetkitDataUpdateCoordinator], Generic[_DevicesT]):
    """Petkit Entity class."""

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

        if self.device.device_type:
            device_type = self.device.device_type
        else:
            device_type = "Unknown"

        device_info = DeviceInfo(
            identifiers={(DOMAIN, self.device.sn)},
            manufacturer="Petkit",
            model=f"{PETKIT_DEVICES_MAPPING.get(device_type.lower(), 'Unknown Device')}",
            model_id=device_type.upper(),
            name=self.device.name,
        )

        if hasattr(self.device, CONNECTION_NETWORK_MAC) and self.device.mac is not None:
            device_info["connections"] = {(CONNECTION_NETWORK_MAC, self.device.mac)}

        if hasattr(self.device, "firmware") and self.device.firmware is not None:
            device_info["sw_version"] = str(self.device.firmware)

        if hasattr(self.device, "hardware") and self.device.hardware is not None:
            device_info["hw_version"] = str(self.device.hardware)

        if hasattr(self.device, "sn") and self.device.sn is not None:
            device_info["serial_number"] = str(self.device.sn)

        return device_info
