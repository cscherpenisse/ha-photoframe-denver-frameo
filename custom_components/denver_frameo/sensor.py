from homeassistant.components.sensor import (
    SensorEntity,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .device import get_device_info


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    coordinator = hass.data[
        "denver_frameo"
    ][entry.entry_id]

    async_add_entities(
        [
            FrameoBrightnessSensor(
                coordinator
            ),

            FrameoForegroundAppSensor(
                coordinator
            ),

            FrameoDisplayStateSensor(
                coordinator
            ),

            FrameoPowerDumpSensor(
                coordinator
            ),
        ]
    )


# --------------------------------------------------
# BASE SENSOR
# --------------------------------------------------

class FrameoBaseSensor(
    CoordinatorEntity,
    SensorEntity,
):
    """Base sensor."""

    def __init__(
        self,
        coordinator,
        unique_suffix,
    ):
        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{unique_suffix}"
        )

        self._attr_device_info = (
            get_device_info(
                coordinator.config_entry
            )
        )

    @property
    def available(self):
        return self.coordinator.data.get(
            "available",
            False,
        )


# --------------------------------------------------
# LED BRIGHTNESS
# --------------------------------------------------

class FrameoBrightnessSensor(
    FrameoBaseSensor,
):
    """Frameo LED brightness."""

    _attr_name = "Frameo LED Brightness"
    _attr_icon = "mdi:brightness-6"

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(
            coordinator,
            "brightness",
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(
            "brightness",
            0,
        )


# --------------------------------------------------
# FOREGROUND APP
# --------------------------------------------------

class FrameoForegroundAppSensor(
    FrameoBaseSensor,
):
    """Foreground app sensor."""

    _attr_name = "Foreground App"
    _attr_icon = "mdi:application"

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(
            coordinator,
            "foreground_app",
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(
            "foreground_app",
            "unknown",
        )


# --------------------------------------------------
# DISPLAY STATE
# --------------------------------------------------

class FrameoDisplayStateSensor(
    FrameoBaseSensor,
):
    """Display ON/OFF sensor."""

    _attr_name = "Display State"

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(
            coordinator,
            "display_state",
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(
            "display_state",
            "OFF",
        )

    @property
    def icon(self):
        state = self.coordinator.data.get(
            "display_state",
            "OFF",
        )

        return (
            "mdi:monitor"
            if state == "ON"
            else "mdi:monitor-off"
        )

    @property
    def extra_state_attributes(self):
        return {
            "screen_on": self.coordinator.data.get(
                "screen_on",
                False,
            ),
        }


# --------------------------------------------------
# POWER DUMP SENSOR
# --------------------------------------------------

class FrameoPowerDumpSensor(
    FrameoBaseSensor,
):
    """ADB dumpsys power debug sensor."""

    _attr_name = "Power Dump"
    _attr_icon = "mdi:android-debug-bridge"

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(
            coordinator,
            "power_dump",
        )

    @property
    def native_value(self):
        dump = self.coordinator.data.get(
            "power_dump",
            "",
        )

        if not dump:
            return "NO DATA"

        if "state=ON" in dump:
            return "ON"

        if "state=OFF" in dump:
            return "OFF"

        return "UNKNOWN"

    @property
    def extra_state_attributes(self):
        return {
            "full_output": self.coordinator.data.get(
                "power_dump",
                "",
            ),
        }
