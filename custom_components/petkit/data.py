"""Custom types for Petkit Smart Devices integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pypetkitapi.containers import Pet
from pypetkitapi.feeder_container import Feeder
from pypetkitapi.litter_container import Litter
from pypetkitapi.water_fountain_container import WaterFountain

if TYPE_CHECKING:
    from pypetkitapi.client import PetKitClient

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .coordinator import PetkitDataUpdateCoordinator


type PetkitConfigEntry = ConfigEntry[PetkitData]

# Custom types for Petkit Smart Devices integration
type PetkitDevices = Feeder | Litter | WaterFountain | Pet


@dataclass
class PetkitData:
    """Data for the Petkit integration."""

    client: PetKitClient
    coordinator: PetkitDataUpdateCoordinator
    integration: Integration
