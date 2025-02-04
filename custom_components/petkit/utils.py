"""Util functions for the Petkit integration."""

from pypetkitapi import LitterRecord, RecordsItems, WorkState

from .const import EVENT_MAPPING, LOGGER


def map_work_state(work_state: WorkState | None) -> str:
    """Get the state of the litter box.

    Use the 'litter_state' translation table to map the state to a human readable string.
    """

    LOGGER.debug(f"Litter map work_state: {work_state}")

    if work_state is None:
        return "idle"

    def get_safe_warn_status(safe_warn: int, pet_in_time: int) -> str:
        """Get the safe warn status."""
        if safe_warn != 0:
            return {
                1: "pet_entered",
                3: "cover",
            }.get(safe_warn, "system_error")
        return "pet_approach" if pet_in_time == 0 else "pet_using"

    def handle_process_mapping(prefix: str) -> str:
        """Handle the process mapping."""
        major, minor = divmod(work_state.work_process, 10)

        if major == 1:
            return f"{prefix}"
        if major == 2:
            if minor == 2:
                return f"{prefix}_paused_{get_safe_warn_status(work_state.safe_warn, work_state.pet_in_time)}"
            return f"{prefix}_paused"
        if major == 3:
            return "resetting_device"
        if major == 4:
            if minor == 2:
                return f"paused_{get_safe_warn_status(work_state.safe_warn, work_state.pet_in_time)}"
            return "paused"
        return f"{prefix}"

    # Map work_mode to their respective functions
    _WORK_MODE_MAPPING = {
        0: lambda: handle_process_mapping("cleaning"),
        1: lambda: handle_process_mapping("dumping"),
        2: lambda: "odor_removal",
        3: lambda: "resetting",
        4: lambda: "leveling",
        5: lambda: "calibrating",
        6: lambda: "reset_deodorant",
        7: lambda: "light",
        8: lambda: "reset_max_deodorant",
        9: lambda: handle_process_mapping("maintenance"),
    }

    return _WORK_MODE_MAPPING.get(work_state.work_mode, lambda: "idle")()


def get_raw_feed_plan(feeder_records_data) -> str | None:
    """Get the raw feed plan from feeder data."""
    result = []

    if not feeder_records_data:
        LOGGER.debug("No feeder records data found")
        return None

    if feeder_records_data.feed is None:
        LOGGER.debug("No feed data found")
        return None

    for feed in feeder_records_data.feed:
        items = feed.items
        for idx, item in enumerate(items):
            id_incremental = idx
            time_in_seconds = item.time
            hours = time_in_seconds // 3600
            minutes = (time_in_seconds % 3600) // 60

            # Calculate amount
            amount = (
                item.amount
                if item.amount is not None
                else (getattr(item, "amount1", 0) or 0)
                + (getattr(item, "amount2", 0) or 0)
            )

            state = 255  # By default, we assume that the food is pending
            if hasattr(item.state, "err_code"):
                err_code = item.state.err_code
                if err_code == 0:
                    # Everything was OK dispensing food
                    state = 0
                elif err_code == 10:
                    # Food was not dispensed cause SurplusControl skipped it
                    state = 255
                else:
                    # Food was not dispensed cause of other reasons
                    state = 1
            result.append(f"{id_incremental},{hours},{minutes},{amount},{state}")
    return ",".join(result) if result else None


def map_litter_event(litter_event: list[LitterRecord | None]) -> str | None:
    """Return a description of the last event

    Use the 'litter_last_event' translation table to map the state to a human readable string.
    """

    if not isinstance(litter_event, list) or not litter_event:
        return None

    litter_event = litter_event[-1]

    error = litter_event.content.error

    if litter_event.sub_content:
        event_type = litter_event.sub_content[-1].event_type
        result = litter_event.sub_content[-1].content.result
        reason = litter_event.sub_content[-1].content.start_reason
    else:
        return litter_event.enum_event_type

    if event_type not in [5, 6, 7, 8, 10]:
        LOGGER.debug(f"Unknown event type code: {event_type}")
        return "event_type_unknown"

    if event_type == 10:
        name = "Unknown" if litter_event.pet_name is None else litter_event.pet_name
        return f"{name} used the litter box"

    try:
        if event_type == 5 and result == 2:
            return EVENT_MAPPING[event_type][result][reason][error]

        if event_type in [6, 7] and result == 2:
            return EVENT_MAPPING[event_type][result][error]

        if event_type in [8, 5]:
            return EVENT_MAPPING[event_type][result][reason]

        return EVENT_MAPPING[event_type][result]

    except KeyError:
        LOGGER.debug(f"Unknown event type result: {event_type}")
        return f"event_type_{event_type}_unknown"


def get_dispense_status(
    feed_record: RecordsItems,
) -> tuple[str, str, int, int, int, int]:
    """Get the dispense status.

    :param feed_record: RecordsItems
    :return: tuple (source, status, plan_amount1, plan_amount2, disp_amount1, disp_amount2)
    """

    # Init
    plan_amount1 = getattr(feed_record, "amount", 0)
    plan_amount2 = 0
    disp_amount1 = 0
    disp_amount2 = 0

    # Déterminer les montants planifiés si `amount1` et `amount2` existent
    if hasattr(feed_record, "amount1") and hasattr(feed_record, "amount2"):
        plan_amount1 = feed_record.amount1
        plan_amount2 = feed_record.amount2

    # Find the source
    source_mapping = {
        1: "feeding plan",
        3: "manual (source : from application)",
        4: "manual (source : locally from feeder)",
    }
    source = source_mapping.get(feed_record.src, "unknown")

    # Find the status
    if feed_record.status == 1:
        status = "cancelled"
    elif hasattr(feed_record, "state") and feed_record.state is not None:
        state = feed_record.state
        if state.err_code == 0 and state.result == 0:
            status = "dispensed"
        elif state.err_code == 10 and state.result == 8:
            status = "skipped"
        else:
            status = "failed dispense"

        # Determinate the dispensed amount
        disp_amount1 = getattr(state, "real_amount", 0)
        disp_amount1 = getattr(state, "real_amount1", disp_amount1)
        disp_amount2 = getattr(state, "real_amount2", 0)
    else:
        status = "pending"

    return source, status, plan_amount1, plan_amount2, disp_amount1, disp_amount2
