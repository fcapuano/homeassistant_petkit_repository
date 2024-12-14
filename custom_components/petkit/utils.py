""" Util functions for the Petkit integration. """

from math import floor
from pypetkitapi.litter_container import WorkState
from .const import LOGGER


def map_work_state(work_state: WorkState | None):
    """Get the state of the litter box."""
    LOGGER.debug(f"Find work_state for : {work_state}")

    if work_state is None:
        return "idle"

    def get_safe_warn_status(safe_warn, pet_in_time):
        """Get the safe warn status."""
        if safe_warn != 0:
            return {
                1: "pet_entered",
                3: "cover",
            }.get(safe_warn, "system_error")
        return "pet_approach" if pet_in_time == 0 else "pet_using"

    def handle_process_mapping(prefix):
        """Handle the process mapping."""
        work_process = work_state.work_process
        major = int(floor(work_process / 10))
        minor = work_process % 10

        if major == 1:
            return f"{prefix}"
        elif major == 2:
            if minor == 2:
                safe_warn_status = get_safe_warn_status(
                    work_state.safe_warn, work_state.pet_in_time
                )
                return f"{prefix}_paused_{safe_warn_status}"
            return f"{prefix}_paused"
        elif major == 3:
            return "resetting_device"
        elif major == 4:
            if minor == 2:
                safe_warn_status = get_safe_warn_status(
                    work_state.safe_warn, work_state.pet_in_time
                )
                return f"paused_{safe_warn_status}"
            return "paused"
        else:
            return f"{prefix}"

    work_mode_mapping = {
        0: lambda: handle_process_mapping("cleaning"),
        1: lambda: handle_process_mapping("dumping"),
        2: lambda: "unknown",
        3: lambda: "resetting",
        4: lambda: "leveling",
        5: lambda: "calibrating",
        9: lambda: handle_process_mapping("maintenance"),
    }

    work_mode = work_state.work_mode
    if work_mode in work_mode_mapping:
        return work_mode_mapping[work_mode]()
    return "idle"
