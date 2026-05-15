from datetime import timedelta
import hashlib
import logging

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)

from .const import DOMAIN
from .device import get_device_info

LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=10)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [FrameoMediaPlayer(coordinator)]
    )


class FrameoMediaPlayer(MediaPlayerEntity):
    """Denver Frameo media player."""

    _attr_name = "Frameo Screen"
    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON |
        MediaPlayerEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator):
        self.coordinator = coordinator

        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_media"

        self._attr_device_info = get_device_info(
            coordinator.config_entry
        )

        self._media_image = (None, None)
        self._attr_media_image_hash = None

        self._attr_state = MediaPlayerState.OFF

    # -------------------------
    # AVAILABILITY
    # -------------------------

    @property
    def available(self):
        return bool(self.coordinator.data)

    # -------------------------
    # STATE (BELANGRIJK)
    # -------------------------

    @property
    def state(self):
        """Return ON/OFF based on coordinator."""
        if not self.coordinator.data:
            return MediaPlayerState.OFF

        return (
            MediaPlayerState.ON
            if self.coordinator.data.get("screen_on")
            else MediaPlayerState.OFF
        )

    # -------------------------
    # SCREENSHOT
    # -------------------------

    @property
    def media_image(self):
        return self._media_image

    async def async_get_media_image(self):
        return self._media_image

    # -------------------------
    # UPDATE (ALLEEN COORDINATOR)
    # -------------------------

    async def async_update(self):
        """Do NOT do ADB here in final architecture."""

        try:
            await self.coordinator.async_request_refresh()

            data = self.coordinator.data or {}

            image = data.get("screenshot")

            if image:
                self._media_image = (image, "image/png")
                self._attr_media_image_hash = hashlib.sha256(image).hexdigest()[:16]

        except Exception as err:
            LOGGER.warning("Media update failed: %s", err)

    # -------------------------
    # TURN ON/OFF
    # -------------------------

    async def async_turn_on(self):
        await self.coordinator.adb.toggle_screen()

    async def async_turn_off(self):
        await self.coordinator.adb.toggle_screen()

    # -------------------------
    # ATTRIBUTES
    # -------------------------

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}

        return {
            "foreground_app": data.get("foreground_app"),
            "ip_address": self.coordinator.config_entry.data.get("host"),
        }
