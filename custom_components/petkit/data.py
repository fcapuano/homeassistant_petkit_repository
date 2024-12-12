"""Custom types for Petkit Smart Devices integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from pypetkitapi.client import PetKitClient
    from .coordinator import PetkitDataUpdateCoordinator


type PetkitConfigEntry = ConfigEntry[PetkitData]


@dataclass
class PetkitData:
    """Data for the Petkit integration."""

    client: PetKitClient
    coordinator: PetkitDataUpdateCoordinator
    integration: Integration
