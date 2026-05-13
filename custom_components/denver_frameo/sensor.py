from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .device import get_device_info


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["denver_frameo"][entry.entry_id]

    async_add_entities([
        FrameoBrightnessSensor(coordinator),
        FrameoForegroundAppSensor(coordinator),
    ])


class FrameoBrightnessSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Frameo LED Brightness"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_device_info = get_device_info(coordinator.config_entry)
        
    @property
    def native_value(self):
        return self.coordinator.data["brightness"]

class FrameoForegroundAppSensor(
    CoordinatorEntity,
    SensorEntity,
):
    _attr_name = "Foreground App"

    def __init__(self, coordinator):
        super().__init__(coordinator)

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
