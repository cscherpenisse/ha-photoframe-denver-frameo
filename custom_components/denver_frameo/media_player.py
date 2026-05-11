import asyncio
from pathlib import Path

from homeassistant.components.media_player import (
    MediaPlayerEntity,
)
from homeassistant.components.media_player.const import (
    MediaPlayerState,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .device import get_device_info


SCREENSHOT_PATH = "/config/www/frameo_screen.png"


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["denver_frameo"][entry.entry_id]

    async_add_entities([
        FrameoMediaPlayer(coordinator)
    ])


class FrameoMediaPlayer(
    CoordinatorEntity,
    MediaPlayerEntity,
):
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
        return "/local/frameo_screen.png"

    async def async_turn_on(self):
        await self.coordinator.adb.toggle_screen()

    async def async_turn_off(self):
        await self.coordinator.adb.toggle_screen()

    async def async_update(self):
        host = self.coordinator.config_entry.data["host"]

        cmd = (
            f"adb connect {host}:5555 && "
            f"adb exec-out screencap -p "
            f"> {SCREENSHOT_PATH}"
        )

        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        await proc.communicate()

        await super().async_update()
