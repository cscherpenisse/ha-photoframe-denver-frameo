from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import MediaPlayerState
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .device import get_device_info


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["denver_frameo"][entry.entry_id]

    async_add_entities([
        FrameoMediaPlayer(coordinator)
    ])


class FrameoMediaPlayer(CoordinatorEntity, MediaPlayerEntity):
    _attr_name = "Frameo Display"

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_device_info = get_device_info(
            coordinator.config_entry
        )

    @property
    def state(self):
        if self.coordinator.data["is_on"]:
            return MediaPlayerState.ON

        return MediaPlayerState.OFF

    @property
    def media_image_url(self):
        host = self.coordinator.config_entry.data["host"]

        # Fully Kiosk screenshot endpoint
        return (
            f"http://{host}:2323/?cmd=getCurrentImage"
        )

    async def async_turn_on(self):
        await self.coordinator.adb.toggle_screen()

    async def async_turn_off(self):
        await self.coordinator.adb.toggle_screen()
