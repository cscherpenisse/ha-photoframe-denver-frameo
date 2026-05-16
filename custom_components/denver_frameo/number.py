from homeassistant.components.number import (
    NumberEntity,
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
    coordinator = hass.data["denver_frameo"][
        entry.entry_id
    ]

    async_add_entities([
        FrameoScreenBrightness(coordinator)
    ])


class FrameoScreenBrightness(
    CoordinatorEntity,
    NumberEntity,
):
    _attr_name = "Screen Brightness"

    _attr_native_min_value = 0
    _attr_native_max_value = 255
    _attr_native_step = 1

    _attr_mode = "slider"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        
        self._attr_unique_id = (f"{coordinator.config_entry.entry_id}_screen_brightness") 
        self._attr_device_info = get_device_info(
            coordinator.config_entry
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(
            "screen_brightness",
            127,
        )

    async def async_set_native_value(
        self,
        value,
    ):
        await self.coordinator.adb.set_screen_brightness(
            int(value)
        )

        await self.coordinator.async_request_refresh()
