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
# LED BRIGHTNESS
# --------------------------------------------------

class FrameoBrightnessSensor(
    CoordinatorEntity,
    SensorEntity,
):
    """Frameo LED brightness."""

    _attr_name = "Frameo LED Brightness"

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_brightness"
        )

        self._attr_device_info = (
            get_device_info(
                coordinator.config_entry
            )
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(
            "brightness",
            0,
        )

    @property
    def available(self):
        return self.coordinator.data.get(
            "available",
            False,
        )


# --------------------------------------------------
# FOREGROUND APP
# --------------------------------------------------

class FrameoForegroundAppSensor(
    CoordinatorEntity,
    SensorEntity,
):
    """Foreground app sensor."""

    _attr_name = "Foreground App"

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_foreground_app"
        )

        self._attr_device_info = (
            get_device_info(
                coordinator.config_entry
            )
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(
            "foreground_app",
            "unknown",
        )

    @property
    def available(self):
        return self.coordinator.data.get(
            "available",
            False,
        )


# --------------------------------------------------
# DISPLAY STATE
# --------------------------------------------------

class FrameoDisplayStateSensor(
    CoordinatorEntity,
    SensorEntity,
):
    """Display ON/OFF sensor."""

    _attr_name = "Display State"

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_display_state"
        )

        self._attr_device_info = (
            get_device_info(
                coordinator.config_entry
            )
        )

    @property
    def native_value(self):
        screen_on = self.coordinator.data.get(
            "screen_on",
            False,
        )

        return (
            "ON"
            if screen_on
            else "OFF"
        )

    @property
    def icon(self):
        screen_on = self.coordinator.data.get(
            "screen_on",
            False,
        )

        return (
            "mdi:monitor"
            if screen_on
            else "mdi:monitor-off"
        )

    @property
    def available(self):
        return self.coordinator.data.get(
            "available",
            False,
        )

# --------------------------------------------------
# POWER DUMP DEBUG SENSOR
# --------------------------------------------------

class FrameoPowerDumpSensor(
    CoordinatorEntity,
    SensorEntity,
):
    """ADB dumpsys power debug sensor."""

    _attr_name = "Power Dump"

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_power_dump"
        )

        self._attr_device_info = (
            get_device_info(
                coordinator.config_entry
            )
        )

        self._state = "unknown"
        
        self._full_output = "No data yet"
        
    @property
    def native_value(self):
        return self._state

    async def async_update(self):
        """Fetch dumpsys power."""

        try:
            output = await self.coordinator.adb.shell(
                "dumpsys power"
            )

            self._full_output = str(output)

            self._state = (
                "ON"
                if "state=ON" in self._full_output
                else "OFF"
            )
        
        except Exception as err:
            self._state = f"ERROR: {err}"

    @property
    def extra_state_attributes(self):
        return {
            "full_output": self._full_output,
        }

    @property
    def available(self):
        return self.coordinator.data.get(
            "available",
            False,
        )
