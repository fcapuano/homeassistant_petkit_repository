"""Sensor platform for Petkit Smart Devices integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from pypetkitapi import (
    D4S,
    DEVICES_FEEDER,
    DEVICES_LITTER_BOX,
    K2,
    T4,
    T6,
    Feeder,
    Litter,
    Pet,
    Purifier,
    WaterFountain,
)

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
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume,
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

    entity_picture: callable[Any] | None = None


SENSOR_MAPPING: dict[
    type[Feeder | Litter | WaterFountain | Pet], list[PetKitSensorDesc]
] = {
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
                device.state.error_msg
                if device.state.error_msg is not None
                else "No error"
            ),
            force_add=DEVICES_FEEDER,
        ),
        PetKitSensorDesc(
            key="Times dispensed",
            translation_key="times_dispensed",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.state.feed_state.times,
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
            value=lambda device: device.state.feed_state.eat_amount_total,  # D3
        ),
        PetKitSensorDesc(
            key="Times eaten",
            translation_key="times_eaten",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: (
                len(device.state.feed_state.eat_times)
                if device.state.feed_state.eat_times is not None
                else None
            ),
            ignore_types=[D4S],
        ),
        PetKitSensorDesc(
            key="Times eaten",
            translation_key="times_eaten",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.state.feed_state.eat_count,
            only_for_types=[D4S],
        ),
        PetKitSensorDesc(
            key="Food in bowl",
            translation_key="food_in_bowl",
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
            value=lambda device: (
                max(0, min(100, device.state.bowl))
                if device.state.bowl is not None
                else None
            ),
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
            key="Smart spray battery",
            translation_key="smart_spray_battery",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.BATTERY,
            native_unit_of_measurement=PERCENTAGE,
            value=lambda device: device.k3_device.battery,
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
            key="Litter level",
            translation_key="litter_level",
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
                device.state.error_msg
                if device.state.error_msg is not None
                else "No error"
            ),
            force_add=DEVICES_LITTER_BOX,
        ),
        PetKitSensorDesc(
            key="State",
            translation_key="litter_state",
            value=lambda device: map_work_state(device.state.work_state),
        ),
        PetKitSensorDesc(
            key="Litter last event",
            translation_key="litter_last_event",
            value=lambda device: map_litter_event(device.device_records),
        ),
        PetKitSensorDesc(
            key="Deodorant left days",
            translation_key="deodorant_left_days",
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.DAYS,
            value=lambda device: device.state.deodorant_left_days,
        ),
        PetKitSensorDesc(
            key="Spray deodorant liquid",
            translation_key="spray_deodorant_liquid",
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=PERCENTAGE,
            value=lambda device: (
                device.state.liquid
                if device.state.liquid is not None and 0 <= device.state.liquid <= 100
                else None
            ),
        ),
        PetKitSensorDesc(
            key="Times used",
            translation_key="times_used",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.device_stats.times,
        ),
        PetKitSensorDesc(
            key="Total time",
            translation_key="total_time",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value=lambda device: device.device_stats.total_time,
        ),
        PetKitSensorDesc(
            key="Average time",
            translation_key="average_time",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value=lambda device: device.device_stats.avg_time,
        ),
        PetKitSensorDesc(
            key="Last used by",
            translation_key="last_used_by",
            value=lambda device: (
                device.device_stats.statistic_info[-1].pet_name
                if device.device_stats.statistic_info
                else None
            ),
            only_for_types=[T4],
        ),
        PetKitSensorDesc(
            key="Last used by",
            translation_key="last_used_by",
            value=lambda device: (
                device.device_pet_graph_out[-1].pet_name
                if device.device_pet_graph_out
                else None
            ),
            only_for_types=[T6],
        ),
        PetKitSensorDesc(
            key="Total package",
            translation_key="total_package",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.package_total_count,
        ),
        PetKitSensorDesc(
            key="Package used",
            translation_key="package_used",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.package_used_count,
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
            value=lambda device: (
                len(device.device_records)
                if isinstance(device.device_records, list)
                else None
            ),
        ),
    ],
    Pet: [
        PetKitSensorDesc(
            key="Pet last weight measurement",
            translation_key="pet_last_weight_measurement",
            entity_picture=lambda pet: pet.avatar,
            device_class=SensorDeviceClass.WEIGHT,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfMass.KILOGRAMS,
            value=lambda pet: round((pet.last_measured_weight / 1000), 2),
        ),
        PetKitSensorDesc(
            key="Pet last use duration",
            translation_key="pet_last_use_duration",
            entity_picture=lambda pet: pet.avatar,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value=lambda pet: pet.last_duration_usage,
        ),
        PetKitSensorDesc(
            key="Pet last device used",
            translation_key="pet_last_device_used",
            entity_picture=lambda pet: pet.avatar,
            value=lambda pet: pet.last_device_used,
        ),
        PetKitSensorDesc(
            key="Pet last use date",
            translation_key="pet_last_use_date",
            entity_picture=lambda pet: pet.avatar,
            value=lambda pet: (
                datetime.fromtimestamp(pet.last_litter_usage)
                if pet.last_litter_usage != 0
                else None
            ),
        ),
    ],
    Purifier: [
        PetKitSensorDesc(
            key="Humidity",
            translation_key="humidity",
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.HUMIDITY,
            value=lambda device: round(device.state.humidity / 10),
        ),
        PetKitSensorDesc(
            key="Temperature",
            translation_key="temperature",
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            value=lambda device: round(device.state.temp / 10),
        ),
        PetKitSensorDesc(
            key="Air purified",
            translation_key="air_purified",
            state_class=SensorStateClass.TOTAL,
            native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
            device_class=SensorDeviceClass.VOLUME,
            value=lambda device: round(device.state.refresh),
        ),
        PetKitSensorDesc(
            key="Error message",
            translation_key="error_message",
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: (
                device.state.error_msg
                if hasattr(device.state, "error_msg")
                and device.state.error_msg is not None
                else "No error"
            ),
            force_add=[K2],
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
            key="Purifier liquid",
            translation_key="purifier_liquid",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=PERCENTAGE,
            value=lambda device: (
                device.state.liquid
                if device.state.liquid is not None and 0 <= device.state.liquid <= 100
                else None
            ),
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
        PetkitSensor(
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


class PetkitSensor(PetkitEntity, SensorEntity):
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
    def entity_picture(self) -> str | None:
        """Grab associated pet picture."""

        if self.entity_description.entity_picture:
            return self.entity_description.entity_picture(self.device)
        return None

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the binary_sensor."""
        return f"{self.device.device_nfo.device_type}_{self.device.sn}_{self.entity_description.key}"

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        return self.entity_description.native_unit_of_measurement
