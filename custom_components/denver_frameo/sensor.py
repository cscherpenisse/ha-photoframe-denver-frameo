from .device import get_device_info
self._attr_device_info = get_device_info(coordinator.config_entry)

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["denver_frameo"][entry.entry_id]

    async_add_entities([
        FrameoBrightnessSensor(coordinator)
    ])


class FrameoBrightnessSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Frameo LED Brightness"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):
        return self.coordinator.data["brightness"]
