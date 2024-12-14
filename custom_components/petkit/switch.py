"""Switch platform for Petkit Smart Devices integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import (SwitchEntity,
                                             SwitchEntityDescription)
from homeassistant.const import EntityCategory
from pypetkitapi.command import DeviceCommand, LitterBoxCommand
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
class PetKitSwitchDesc(PetKitDescSensorBase, SwitchEntityDescription):
    """A class that describes sensor entities."""

    turn_on: Callable[[Any, Any], Any] | None = None
    turn_off: Callable[[Any, Any], Any] | None = None


SWITCH_MAPPING: dict[type[Feeder | Litter | WaterFountain], list[PetKitSwitchDesc]] = {
    Feeder: [
        PetKitSwitchDesc(
            key="Indicator light",
            translation_key="indicator_light",
            value=lambda device: device.settings.light_mode,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"lightMode": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"lightMode": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Child lock",
            translation_key="child_lock",
            value=lambda device: device.settings.manual_lock,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"manualLock": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"manualLock": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Shortage alarm",
            translation_key="shortage_alarm",
            value=lambda device: device.settings.food_warn,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"foodWarn": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"foodWarn": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Feed tone",
            translation_key="feed_tone",
            value=lambda device: device.settings.feed_tone,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"feedTone": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"feedTone": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Feed sound",
            translation_key="feed_sound",
            value=lambda device: device.settings.feed_sound,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"feedSound": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"feedSound": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Dispensing notif",
            translation_key="dispensing_notif",
            value=lambda device: device.settings.feed_notify,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"feedNotify": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"feedNotify": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Refill notif",
            translation_key="refill_notif",
            value=lambda device: device.settings.food_notify,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"foodNotify": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"foodNotify": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Pet visit notif",
            translation_key="pet_visit_notif",
            value=lambda device: device.settings.pet_notify,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"petNotify": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"petNotify": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Pet eat notif",
            translation_key="pet_eat_notif",
            value=lambda device: device.settings.eat_notify,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"eatNotify": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"eatNotify": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Surplus control",
            translation_key="surplus_control",
            value=lambda device: device.settings.surplus_control,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"surplusControl": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"surplusControl": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="System notification",
            translation_key="system_notification",
            value=lambda device: device.settings.system_sound_enable,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"systemSoundEnable": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"systemSoundEnable": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Camera",
            translation_key="camera",
            value=lambda device: device.settings.camera,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"camera": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"camera": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Low battery notif",
            translation_key="low_battery_notif",
            value=lambda device: device.settings.low_battery_notify,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"lowBatteryNotify": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"lowBatteryNotify": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Microphone",
            translation_key="microphone",
            value=lambda device: device.settings.microphone,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"microphone": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"microphone": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Night vision",
            translation_key="night_vision",
            value=lambda device: device.settings.night,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"night": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"night": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Voice dispense",
            translation_key="voice_dispense",
            value=lambda device: device.settings.sound_enable,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"soundEnable": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"soundEnable": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Do not disturb",
            translation_key="do_not_disturb",
            value=lambda device: device.settings.disturb_mode,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"disturbMode": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"disturbMode": 0}
            ),
        ),
    ],
    Litter: [
        PetKitSwitchDesc(
            key="Auto odor",
            translation_key="auto_odor",
            value=lambda device: device.settings.auto_refresh,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"autoRefresh": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"autoRefresh": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Auto clean",
            translation_key="auto_clean",
            value=lambda device: device.settings.auto_work,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"autoWork": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"autoWork": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Avoid repeat",
            translation_key="avoid_repeat",
            value=lambda device: device.settings.avoid_repeat,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"avoidRepeat": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"avoidRepeat": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Do not disturb",
            translation_key="do_not_disturb",
            value=lambda device: device.settings.disturb_mode,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"disturbMode": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"disturbMode": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Periodic cleaning",
            translation_key="periodic_cleaning",
            value=lambda device: device.settings.fixed_time_clear,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"fixedTimeClear": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"fixedTimeClear": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Periodic odor",
            translation_key="periodic_odor",
            value=lambda device: device.settings.fixed_time_refresh,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"fixedTimeRefresh": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"fixedTimeRefresh": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Kitten mode",
            translation_key="kitten_mode",
            value=lambda device: device.settings.kitten,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"kitten": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"kitten": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Display",
            translation_key="display",
            value=lambda device: device.settings.light_mode,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"lightMode": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"lightMode": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Child lock lb",
            translation_key="child_lock",
            value=lambda device: device.settings.manual_lock,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"manualLock": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"manualLock": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Light weight",
            translation_key="light_weight",
            value=lambda device: device.settings.underweight,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"underweight": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.send_api_request(
                device.id, DeviceCommand.UPDATE_SETTING, {"underweight": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Power",
            translation_key="power",
            value=lambda device: device.state.power,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.control_litter_box(
                device.id, LitterBoxCommand.POWER
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.control_litter_box(
                device.id, LitterBoxCommand.POWER
            ),
        ),
        PetKitSwitchDesc(
            key="Cont rotation",
            translation_key="cont_rotation",
            value=lambda device: device.settings.downpos,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.update_litter_box_settings(
                device.id, DeviceCommand.UPDATE_SETTING, {"downpos": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.update_litter_box_settings(
                device.id, DeviceCommand.UPDATE_SETTING, {"downpos": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Deep cleaning",
            translation_key="deep_cleaning",
            value=lambda device: device.settings.deep_clean,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.update_litter_box_settings(
                device.id, DeviceCommand.UPDATE_SETTING, {"deepClean": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.update_litter_box_settings(
                device.id, DeviceCommand.UPDATE_SETTING, {"deepClean": 0}
            ),
        ),
        PetKitSwitchDesc(
            key="Deep deodor",
            translation_key="deep_deodor",
            value=lambda device: device.settings.deep_refresh,
            entity_category=EntityCategory.CONFIG,
            turn_on=lambda api,
            device: api.config_entry.runtime_data.client.update_litter_box_settings(
                device.id, DeviceCommand.UPDATE_SETTING, {"deepRefresh": 1}
            ),
            turn_off=lambda api,
            device: api.config_entry.runtime_data.client.update_litter_box_settings(
                device.id, DeviceCommand.UPDATE_SETTING, {"deepRefresh": 0}
            ),
        ),
    ],
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

    entity_description: PetKitSwitchDesc

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
        self.device = device

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the binary_sensor."""
        return (
            f"{self.device.device_type}_{self.device.sn}_{self.entity_description.key}"
        )

    @property
    def is_on(self) -> bool | None :
        """Return true if the switch is on."""
        updated_device = self.coordinator.data.get(self.device.id)
        if updated_device and self.entity_description.value:
            return bool(self.entity_description.value(updated_device))
        return None

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the switch."""
        LOGGER.debug("Turn ON")
        await self.entity_description.turn_on(self.coordinator, self.device)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the switch."""
        LOGGER.debug("Turn OFF")
        await self.entity_description.turn_off(self.coordinator, self.device)
        await self.coordinator.async_request_refresh()
