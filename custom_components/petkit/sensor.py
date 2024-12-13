"""Sensor platform for Petkit Smart Devices integration."""

from __future__ import annotations

from datetime import datetime
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

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import PetkitDataUpdateCoordinator
    from .data import PetkitConfigEntry


class PetKitSensorDesc(PetKitDescSensorBase, SensorEntityDescription):
    """A class that describes sensor entities."""

    options: list[str] | None = None
    state_class: SensorStateClass | None = None
    suggested_display_precision: int | None = None
    suggested_unit_of_measurement: str | None = None


SENSOR_MAPPING: dict[type[Feeder | Litter | WaterFountain], list[PetKitSensorDesc]] = {
    Feeder: [
        PetKitSensorDesc(
            key="device_status",
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: DEVICE_STATUS_MAP.get(
                device.state.pim, "Unknown Status"
            ),
        ),
        PetKitSensorDesc(
            key="desiccant_left_days",
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.DAYS,
            value=lambda device: device.state.desiccant_left_days,
        ),
        PetKitSensorDesc(
            key="battery_power",
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: BATTERY_LEVEL_MAP.get(
                device.state.battery_status, "Unknown Battery Status"
            ),
        ),
        PetKitSensorDesc(
            key="rssi",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.SIGNAL_STRENGTH,
            native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            value=lambda device: device.state.wifi.rsq,
        ),
        PetKitSensorDesc(
            key="error_message",
            entity_category=EntityCategory.DIAGNOSTIC,
            # TODO : Check if this is the correct working on error message
            value=lambda device: (
                device.state.error_msg if "error_msg" in device.state else "no_error"
            ),
        ),
        PetKitSensorDesc(
            key="times_dispensed_d3",
            translation_key="times_dispensed",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.state.feed_state.feed_times,
            only_for_types=[D3],
        ),
        PetKitSensorDesc(
            key="times_dispensed",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.state.feed_state.times,
            ignore_types=[D3],
        ),
        PetKitSensorDesc(
            key="total_planned",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfMass.GRAMS,
            value=lambda device: device.state.feedState.plan_amount_total,
        ),
        PetKitSensorDesc(
            key="planned_dispensed",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfMass.GRAMS,
            value=lambda device: device.state.feedState.planRealAmountTotal,
        ),
        PetKitSensorDesc(
            key="total_dispensed",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfMass.GRAMS,
            value=lambda device: device.state.feedState.realAmountTotal,
        ),
        PetKitSensorDesc(
            key="manual_dispensed",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfMass.GRAMS,
            value=lambda device: device.state.feedState.add_amount_total,
        ),
        PetKitSensorDesc(
            key="amount_eaten",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfMass.GRAMS,
            value=lambda device: device.state.feed_state.eat_amount_total,
        ),
        PetKitSensorDesc(
            key="times_eaten",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=None,  # No unit of measurement for times eaten
            value=lambda device: (
                device.state.feed_state.eat_count
                if device.device_type == D4S
                else len(device.state.feedState.eat_times)
            ),
        ),
        PetKitSensorDesc(
            key="food_in_bowl",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfMass.GRAMS,
            value=lambda device: device.state.weight,
        ),
        PetKitSensorDesc(
            key="avg_eating_time",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            value=lambda device: device.state.feed_state.eat_avg,
        ),
        PetKitSensorDesc(
            key="manual_dispensed_hopper_1",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.state.feed_state.add_amount_total1,
        ),
        PetKitSensorDesc(
            key="manual_dispensed_hopper_2",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.state.feed_state.add_amount_total2,
        ),
        PetKitSensorDesc(
            key="total_planned_hopper_1",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.state.feed_state.plan_amount_total1,
        ),
        PetKitSensorDesc(
            key="total_planned_hopper_2",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: device.state.feed_state.plan_amount_total2,
        ),
        PetKitSensorDesc(
            key="planned_dispensed_hopper_1",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value=lambda device: device.state.feed_state.plan_real_amount_total1,
        ),
        PetKitSensorDesc(
            key="planned_dispensed_hopper_2",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value=lambda device: device.state.feed_state.plan_real_amount_total2,
        ),
        PetKitSensorDesc(
            key="total_dispensed_hopper_1",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value=lambda device: device.state.feed_state.real_amount_total1,
        ),
        PetKitSensorDesc(
            key="total_dispensed_hopper_2",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value=lambda device: device.state.feed_state.real_amount_total2,
        ),
        PetKitSensorDesc(
            key="food_bowl_percentage",
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=PERCENTAGE,
            value=lambda device: max(0, min(100, device.state.bowl)),
        ),
        PetKitSensorDesc(
            key="end_date_care_plus_subscription",
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: datetime.utcfromtimestamp(
                device.cloud_product.work_indate
            ).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        PetKitSensorDesc(
            key="food_left",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=PERCENTAGE,
            value=lambda device: device.state.percent,
        ),
    ],
    Litter: [
        # PetKitSensorDesc(
        #     key="deodorizer_level",
        #     icon=lambda device: 'mdi:air-filter' if device.device_type == T4 else 'mdi:spray-bottle',
        #     entity_category=EntityCategory.DIAGNOSTIC,
        #     state_class=SensorStateClass.MEASUREMENT,
        #     native_unit_of_measurement=lambda device: UnitOfTime.DAYS if device.device_type == T4 else PERCENTAGE,
        #     value=lambda device: device.state.deodorant_left_days if device.device_type == T4 else device.state.liquid,
        # ),
        PetKitSensorDesc(
            key="litter_level",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=PERCENTAGE,
            value=lambda device: device.state.sand_percent,
        ),
        PetKitSensorDesc(
            key="litter_weight",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfMass.KILOGRAMS,
            value=lambda device: round((device.state.sand_weight / 1000), 1),
        ),
        PetKitSensorDesc(
            key="rssi",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            value=lambda device: device.state.wifi.rsq,
        ),
        PetKitSensorDesc(
            key="error_message",
            entity_category=EntityCategory.DIAGNOSTIC,
            value=lambda device: (
                device.state.error_msg if "error_msg" in device.state else "no_error"
            ),
        ),
    ],
    WaterFountain: [
        PetKitSensorDesc(
            key="today_pump_run_time",
            device_class=SensorDeviceClass.ENERGY,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            value=lambda device: round(
                ((0.75 * int(device.today_pump_run_time)) / 3600000), 4
            ),
        ),
        PetKitSensorDesc(
            key="last_update",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.TIMESTAMP,
            value=lambda device: datetime.fromisoformat(
                device.update_at.replace(".000Z", "+00:00")
            ),
        ),
        PetKitSensorDesc(
            key="filter_percent",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=PERCENTAGE,
            value=lambda device: device.filter_percent,
        ),
        PetKitSensorDesc(
            key="purified_water",
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            value=lambda device: int(
                ((1.5 * int(device.today_pump_run_time)) / 60) / 2.0
            ),
        ),
    ],
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PetkitConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors using config entry."""
    devices = (
        entry.runtime_data.client.device_list
    )  # Assuming devices are stored in runtime_data
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
    """Petkit Smart Devices Sensor class."""

    entity_description: PetKitSensorDesc

    def __init__(
        self,
        coordinator: PetkitDataUpdateCoordinator,
        entity_description: PetKitSensorDesc,
        device: Feeder | Litter | WaterFountain,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, device)
        self.entity_description = entity_description
        self._device = device

    @property
    def native_value(self) -> Any:
        """Return the native value of the sensor."""
        if self.entity_description.value:
            return self.entity_description.value(self._device)
        return None

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the binary_sensor."""
        return (
            f"{self._device.device_type}_{self.device.sn}_{self.entity_description.key}"
        )

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        return self.entity_description.unit_of_measurement
