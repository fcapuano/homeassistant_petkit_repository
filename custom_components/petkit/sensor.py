"""Sensor platform for Petkit Smart Devices integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from pypetkitapi.const import D3, D4S
from pypetkitapi.feeder_container import Feeder
from pypetkitapi.litter_container import Litter
from pypetkitapi.water_fountain_container import WaterFountain

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfEnergy,
    UnitOfMass,
    UnitOfTime,
)

from .const import BATTERY_LEVEL_MAP, DEVICE_STATUS_MAP
from .entity import PetKitDescSensorBase, PetkitEntity
from .utils import get_raw_feed_plan, map_litter_event, map_work_state

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import PetkitDataUpdateCoordinator
    from .data import PetkitConfigEntry


@dataclass(frozen=True, kw_only=True)
class PetKitSensorDesc(PetKitDescSensorBase, SensorEntityDescription):
    """A class that describes sensor entities."""


SENSOR_MAPPING: dict[type[Feeder | Litter | WaterFountain], list[PetKitSensorDesc]] = {
    Feeder: [
        PetKitSensorDesc(
            key="Device status",
            translation_key="device_status",
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: DEVICE_STATUS_MAP.get(
                device.state.pim, "Unknown Status"
            ),
        ),
        PetKitSensorDesc(
            key="Desiccant left days",
            translation_key="desiccant_left_days",
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.DAYS,
            value=lambda device: device.state.desiccant_left_days,
        ),
        PetKitSensorDesc(
            key="Battery level",
            translation_key="battery_level",
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: (
                BATTERY_LEVEL_MAP.get(device.state.battery_status, "Unknown")
                if device.state.pim == 2
                else "Not in use"
            ),
        ),
        PetKitSensorDesc(
            key="Rssi",
            translation_key="rssi",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.SIGNAL_STRENGTH,
            native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            value=lambda device: device.state.wifi.rsq,
        ),
        PetKitSensorDesc(
            key="Error message",
            translation_key="error_message",
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: (
                device.state.error_msg if "error_msg" in device.state else "no_error"
            ),
        ),
        PetKitSensorDesc(
            key="Times dispensed d3",
            translation_key="times_dispensed",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.state.feed_state.feed_times,
            only_for_types=[D3],
        ),
        PetKitSensorDesc(
            key="Times dispensed",
            translation_key="times_dispensed",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.state.feed_state.times,
            ignore_types=[D3],
        ),
        PetKitSensorDesc(
            key="Total planned",
            translation_key="total_planned",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfMass.GRAMS,
            value=lambda device: device.state.feed_state.plan_amount_total,
        ),
        PetKitSensorDesc(
            key="Planned dispensed",
            translation_key="planned_dispensed",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfMass.GRAMS,
            value=lambda device: device.state.feed_state.plan_real_amountTotal,
        ),
        PetKitSensorDesc(
            key="Total dispensed",
            translation_key="total_dispensed",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfMass.GRAMS,
            value=lambda device: device.state.feed_state.real_amount_total,
        ),
        PetKitSensorDesc(
            key="Manual dispensed",
            translation_key="manual_dispensed",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfMass.GRAMS,
            value=lambda device: device.state.feed_state.add_amount_total,
        ),
        PetKitSensorDesc(
            key="Amount eaten",
            translation_key="amount_eaten",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfMass.GRAMS,
            value=lambda device: device.state.feed_state.eat_amount_total,
        ),
        PetKitSensorDesc(
            key="Times eaten",
            translation_key="times_eaten",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: (
                device.state.feed_state.eat_count
                if device.device_type == D4S
                else len(device.state.feed_state.eat_times)
            ),
        ),
        PetKitSensorDesc(
            key="Food in bowl",
            translation_key="food_in_bowl",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfMass.GRAMS,
            value=lambda device: device.state.weight,
        ),
        PetKitSensorDesc(
            key="Avg eating time",
            translation_key="avg_eating_time",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value=lambda device: device.state.feed_state.eat_avg,
        ),
        PetKitSensorDesc(
            key="Manual dispensed hopper 1",
            translation_key="manual_dispensed_hopper_1",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.state.feed_state.add_amount_total1,
        ),
        PetKitSensorDesc(
            key="Manual dispensed hopper 2",
            translation_key="manual_dispensed_hopper_2",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.state.feed_state.add_amount_total2,
        ),
        PetKitSensorDesc(
            key="Total planned hopper 1",
            translation_key="total_planned_hopper_1",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.state.feed_state.plan_amount_total1,
        ),
        PetKitSensorDesc(
            key="Total planned hopper 2",
            translation_key="total_planned_hopper_2",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.state.feed_state.plan_amount_total2,
        ),
        PetKitSensorDesc(
            key="Planned dispensed hopper 1",
            translation_key="planned_dispensed_hopper_1",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value=lambda device: device.state.feed_state.plan_real_amount_total1,
        ),
        PetKitSensorDesc(
            key="Planned dispensed hopper 2",
            translation_key="planned_dispensed_hopper_2",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value=lambda device: device.state.feed_state.plan_real_amount_total2,
        ),
        PetKitSensorDesc(
            key="Total dispensed hopper 1",
            translation_key="total_dispensed_hopper_1",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value=lambda device: device.state.feed_state.real_amount_total1,
        ),
        PetKitSensorDesc(
            key="Total dispensed hopper 2",
            translation_key="total_dispensed_hopper_2",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value=lambda device: device.state.feed_state.real_amount_total2,
        ),
        PetKitSensorDesc(
            key="Food bowl percentage",
            translation_key="food_bowl_percentage",
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=PERCENTAGE,
            value=lambda device: max(0, min(100, device.state.bowl)),
        ),
        PetKitSensorDesc(
            key="End date care plus subscription",
            translation_key="end_date_care_plus_subscription",
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: datetime.fromtimestamp(
                device.cloud_product.work_indate, tz=timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        PetKitSensorDesc(
            key="Food left",
            translation_key="food_left",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=PERCENTAGE,
            value=lambda device: device.state.percent,
        ),
        PetKitSensorDesc(
            key="RAW distribution data",
            translation_key="raw_distribution_data",
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: get_raw_feed_plan(device.device_records),
        ),
    ],
    Litter: [
        PetKitSensorDesc(
            key="Device status",
            translation_key="device_status",
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: DEVICE_STATUS_MAP.get(
                device.state.pim, "Unknown Status"
            ),
        ),
        PetKitSensorDesc(
            key="Litter level",
            translation_key="litter_level",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=PERCENTAGE,
            value=lambda device: device.state.sand_percent,
        ),
        PetKitSensorDesc(
            key="Litter weight",
            translation_key="litter_weight",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfMass.KILOGRAMS,
            value=lambda device: round((device.state.sand_weight / 1000), 1),
        ),
        PetKitSensorDesc(
            key="Rssi",
            translation_key="rssi",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            value=lambda device: device.state.wifi.rsq,
        ),
        PetKitSensorDesc(
            key="Error message",
            translation_key="error_message",
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: (
                device.state.error_msg if "error_msg" in device.state else "no_error"
            ),
        ),
        PetKitSensorDesc(
            key="State",
            translation_key="litter_state",
            value=lambda device: map_work_state(device.state.work_state),
        ),
        PetKitSensorDesc(
            key="Litter last event",
            translation_key="litter_last_event",
            value=lambda device: map_litter_event(device.device_records[-1]),
        ),
    ],
    WaterFountain: [
        PetKitSensorDesc(
            key="Today pump run time",
            translation_key="today_pump_run_time",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.ENERGY,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            value=lambda device: round(
                ((0.75 * int(device.today_pump_run_time)) / 3600000), 4
            ),
        ),
        PetKitSensorDesc(
            key="Last update",
            translation_key="last_update",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.TIMESTAMP,
            value=lambda device: datetime.fromisoformat(
                device.update_at.replace(".000Z", "+00:00")
            ),
        ),
        PetKitSensorDesc(
            key="Filter percent",
            translation_key="filter_percent",
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=PERCENTAGE,
            value=lambda device: device.filter_percent,
        ),
        PetKitSensorDesc(
            key="Purified water",
            translation_key="purified_water",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: int(
                ((1.5 * int(device.today_pump_run_time)) / 60) / 2.0
            ),
        ),
        PetKitSensorDesc(
            key="Drink times",
            translation_key="drink_times",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: len(device.device_records),
        ),
    ],
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PetkitConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary_sensors using config entry."""
    devices = entry.runtime_data.client.petkit_entities.values()
    entities = [
        PetkitBinarySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
            device=device,
        )
        for device in devices
        for device_type, entity_descriptions in SENSOR_MAPPING.items()
        if isinstance(device, device_type)
        for entity_description in entity_descriptions
        if entity_description.is_supported(device)  # Check if the entity is supported
    ]
    async_add_entities(entities)


class PetkitBinarySensor(PetkitEntity, SensorEntity):
    """Petkit Smart Devices BinarySensor class."""

    entity_description: PetKitSensorDesc

    def __init__(
        self,
        coordinator: PetkitDataUpdateCoordinator,
        entity_description: PetKitSensorDesc,
        device: Feeder | Litter | WaterFountain,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, device)
        self.coordinator = coordinator
        self.entity_description = entity_description
        self.device = device

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        device_data = self.coordinator.data.get(self.device.id)
        if device_data:
            return self.entity_description.value(device_data)
        return None

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the binary_sensor."""
        return (
            f"{self.device.device_type}_{self.device.sn}_{self.entity_description.key}"
        )

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        return self.entity_description.native_unit_of_measurement
