from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["denver_frameo"][entry.entry_id]

    async_add_entities([
        FrameoLedLight(coordinator)
    ])


class FrameoLedLight(CoordinatorEntity, LightEntity):
    _attr_name = "Frameo LEDs"
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def is_on(self):
        return self.coordinator.data["is_on"]

    @property
    def brightness(self):
        return self.coordinator.data["brightness"]

    @property
    def rgb_color(self):
        return self.coordinator.data["rgb"]

    async def async_turn_on(self, **kwargs):
        brightness = kwargs.get(
            ATTR_BRIGHTNESS,
            self.brightness or 95,
        )

        rgb = kwargs.get(
            ATTR_RGB_COLOR,
            self.rgb_color or (255, 255, 255),
        )

        r, g, b = rgb

        await self.coordinator.adb.set_led_state(
            brightness,
            r,
            g,
            b,
        )

        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.adb.set_led_state(0, 0, 0, 0)

        await self.coordinator.async_request_refresh()
